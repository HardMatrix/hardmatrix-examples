// tensor.c — Linux kernel driver for Vector Adder Machine (VAM)
// Register layout matches VAM hardware: instruction + status + vector register file
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/of.h>
#include <linux/io.h>
#include <linux/miscdevice.h>
#include <linux/fs.h>
#include <linux/uaccess.h>
#include <linux/mutex.h>
#include <linux/vmalloc.h>
#include <linux/delay.h>
#include <linux/err.h>
#include <linux/version.h>
#include <linux/jiffies.h>
#include "../../../include/api.h"

// --- VAM Hardware Register Map ---
#define VAM_REG_INSTRUCTION  0x00
#define VAM_REG_STATUS       0x04
#define VAM_REG_VEC_BASE     0x100
#define VAM_REG_VEC_STRIDE   16      // 4 elements x 4 bytes per vector
#define VAM_NUM_ELEMENTS     4
#define VAM_ELEM_BYTES       4

// Address of vector[vec] element[elem]
#define VAM_VEC_ADDR(vec, elem) \
    (VAM_REG_VEC_BASE + (vec) * VAM_REG_VEC_STRIDE + (elem) * VAM_ELEM_BYTES)

// Status register bits
#define STATUS_DONE   (1u << 0)
#define STATUS_ERR    (1u << 1)
#define STATUS_CLEAR  (1u << 2)

// VAM opcodes (matches VectorAdderUnit.scala)
#define VAM_OP_ADD  1
#define VAM_OP_SUB  2

// Instruction encoding: op[7:0] | rega[10:8] | regb[13:11] | dest[16:14]
#define VAM_ENCODE_INSTR(op, rega, regb, dest) \
    (((op) & 0xFF) | (((rega) & 0x7) << 8) | (((regb) & 0x7) << 11) | (((dest) & 0x7) << 14))

// Fixed vector register assignments
#define VEC_A    0
#define VEC_B    1
#define VEC_OUT  2

// Mock regspace (covers 0x100 + 8*16 = 0x180)
#define MOCK_REGSPACE_BYTES  0x200

static bool debug = true;
module_param(debug, bool, 0644);
MODULE_PARM_DESC(debug, "Enable verbose logging");

static bool mock = false;
module_param(mock, bool, 0644);
MODULE_PARM_DESC(mock, "Use mock backend (software compute)");

static bool mock_autocreate = true;
module_param(mock_autocreate, bool, 0644);
MODULE_PARM_DESC(mock_autocreate, "Auto-register platform device when mock=1");

static ushort device_mode = 0660;
module_param(device_mode, ushort, 0644);
MODULE_PARM_DESC(device_mode, "Permissions for /dev/tensor0 (default 0660)");

static inline const char *op_name(u32 op)
{
    switch (op) {
    case TENSOR_OP_VADD_I32: return "VADD_I32";
    case TENSOR_OP_VSUB_I32: return "VSUB_I32";
    default: return "UNKNOWN";
    }
}

// Map tensor_op enum to VAM hardware opcode
static inline u32 tensor_op_to_vam_op(u32 op)
{
    switch (op) {
    case TENSOR_OP_VADD_I32:
        return VAM_OP_ADD;
    case TENSOR_OP_VSUB_I32:
        return VAM_OP_SUB;
    default:
        return 0;
    }
}

struct tensor_dev {
    struct device *dev;
    void __iomem *regs;
    bool is_mock;
    struct mutex lock;
    struct miscdevice misc;
};

static inline void tensor_writel(struct tensor_dev *d, u32 val, u32 off)
{
    if (d->is_mock)
        *(u32 *)((u8 *)d->regs + off) = val;
    else
        iowrite32(val, d->regs + off);
}

static inline u32 tensor_readl(struct tensor_dev *d, u32 off)
{
    if (d->is_mock)
        return *(u32 *)((u8 *)d->regs + off);
    return ioread32(d->regs + off);
}

// Mock compute: decode instruction, compute in software, set status
static void tensor_do_mock_compute(struct tensor_dev *d)
{
    u32 instr = tensor_readl(d, VAM_REG_INSTRUCTION);
    u32 op   = instr & 0xFF;
    u32 rega = (instr >> 8) & 0x7;
    u32 regb = (instr >> 11) & 0x7;
    u32 dest = (instr >> 14) & 0x7;
    u32 i;

    if (debug)
        dev_info(d->dev, "mock: op=%u rega=%u regb=%u dest=%u\n",
                 op, rega, regb, dest);

    if (op != VAM_OP_ADD && op != VAM_OP_SUB) {
        tensor_writel(d, STATUS_DONE | STATUS_ERR, VAM_REG_STATUS);
        return;
    }

    for (i = 0; i < VAM_NUM_ELEMENTS; i++) {
        u32 a = tensor_readl(d, VAM_VEC_ADDR(rega, i));
        u32 b = tensor_readl(d, VAM_VEC_ADDR(regb, i));
        u32 r = (op == VAM_OP_ADD) ? (a + b) : (a - b);
        tensor_writel(d, r, VAM_VEC_ADDR(dest, i));
    }

    tensor_writel(d, STATUS_DONE, VAM_REG_STATUS);
}

static long tensor_ioctl(struct file *f, unsigned int cmd, unsigned long arg)
{
    struct tensor_dev *d = container_of(f->private_data, struct tensor_dev, misc);
    struct tensor_submit s;
    void *ka = NULL, *kb = NULL, *ko = NULL;
    int ret = 0;
    u32 i, vam_op, instr, status;
    size_t bytes;

    if (debug)
        dev_info(d->dev, "ioctl cmd=0x%x\n", cmd);

    switch (cmd) {
    case TENSOR_IOC_RESET:
        mutex_lock(&d->lock);
        tensor_writel(d, STATUS_CLEAR, VAM_REG_STATUS);
        mutex_unlock(&d->lock);
        dev_info(d->dev, "RESET\n");
        return 0;

    case TENSOR_IOC_SUBMIT:
        if (copy_from_user(&s, (void __user *)arg, sizeof(s)))
            return -EFAULT;

        if (s.version != TENSOR_API_VERSION || s.elem_bytes != 4 || s.flags != 0 ||
            s.len == 0 || s.len > TENSOR_MAX_ELEMENTS)
            return -EINVAL;

        vam_op = tensor_op_to_vam_op(s.op);
        if (vam_op == 0)
            return -EINVAL;

        bytes = (size_t)s.len * (size_t)s.elem_bytes;

        if (debug)
            dev_info(d->dev,
                     "SUBMIT op=%s(%u) len=%u bytes=%zu mock=%d\n",
                     op_name(s.op), s.op, s.len, bytes, d->is_mock);

        ka = kvmalloc(bytes, GFP_KERNEL);
        kb = kvmalloc(bytes, GFP_KERNEL);
        ko = kvmalloc(bytes, GFP_KERNEL);
        if (!ka || !kb || !ko) { ret = -ENOMEM; goto out; }

        if (copy_from_user(ka, (void __user *)(uintptr_t)s.a_ptr, bytes) ||
            copy_from_user(kb, (void __user *)(uintptr_t)s.b_ptr, bytes)) {
            ret = -EFAULT;
            goto out;
        }

        mutex_lock(&d->lock);

        // 1. Write vector A to vectors[0], element by element
        for (i = 0; i < s.len; i++)
            tensor_writel(d, ((u32 *)ka)[i], VAM_VEC_ADDR(VEC_A, i));

        // 2. Write vector B to vectors[1]
        for (i = 0; i < s.len; i++)
            tensor_writel(d, ((u32 *)kb)[i], VAM_VEC_ADDR(VEC_B, i));

        // 3. Clear status
        tensor_writel(d, STATUS_CLEAR, VAM_REG_STATUS);

        // 4. Encode and write instruction (triggers compute via swmod)
        instr = VAM_ENCODE_INSTR(vam_op, VEC_A, VEC_B, VEC_OUT);
        tensor_writel(d, instr, VAM_REG_INSTRUCTION);

        // 5. Compute
        if (d->is_mock) {
            tensor_do_mock_compute(d);
        } else {
            unsigned long timeout = msecs_to_jiffies(s.timeout_ms ? s.timeout_ms : 1000);
            unsigned long deadline = jiffies + max(timeout, 1UL);
            for (;;) {
                status = tensor_readl(d, VAM_REG_STATUS);
                if (status & (STATUS_DONE | STATUS_ERR))
                    break;
                if (signal_pending(current)) {
                    ret = -ERESTARTSYS;
                    break;
                }
                if (time_after_eq(jiffies, deadline)) {
                    ret = -ETIMEDOUT;
                    break;
                }
                cpu_relax();
            }
            if (!ret) {
                status = tensor_readl(d, VAM_REG_STATUS);
                if (!(status & (STATUS_DONE | STATUS_ERR)))
                    ret = -ETIMEDOUT;
                else if (status & STATUS_ERR)
                    ret = -EIO;
            }
        }

        // 6. Read status
        status = tensor_readl(d, VAM_REG_STATUS);
        s.status = status;

        if (debug)
            dev_info(d->dev, "DONE ret=%d status=0x%08x\n", ret, status);

        // 7. Read result from vectors[2]
        if (!ret) {
            for (i = 0; i < s.len; i++)
                ((u32 *)ko)[i] = tensor_readl(d, VAM_VEC_ADDR(VEC_OUT, i));
            if (copy_to_user((void __user *)(uintptr_t)s.out_ptr, ko, bytes))
                ret = -EFAULT;
        }

        mutex_unlock(&d->lock);

        if (copy_to_user((void __user *)arg, &s, sizeof(s)))
            ret = -EFAULT;

        goto out;

    default:
        return -ENOTTY;
    }

out:
    kvfree(ka);
    kvfree(kb);
    kvfree(ko);
    return ret;
}

static int tensor_open(struct inode *ino, struct file *f)
{
    return 0;
}

static const struct file_operations tensor_fops = {
    .owner          = THIS_MODULE,
    .open           = tensor_open,
    .unlocked_ioctl = tensor_ioctl,
#if LINUX_VERSION_CODE >= KERNEL_VERSION(6, 12, 0)
    .llseek         = noop_llseek,
#else
    .llseek         = no_llseek,
#endif
};

static int tensor_probe(struct platform_device *pdev)
{
    struct tensor_dev *d;
    int ret;

    d = devm_kzalloc(&pdev->dev, sizeof(*d), GFP_KERNEL);
    if (!d) return -ENOMEM;

    d->dev = &pdev->dev;
    mutex_init(&d->lock);

    d->is_mock = mock;
    if (d->is_mock) {
        d->regs = devm_kzalloc(&pdev->dev, MOCK_REGSPACE_BYTES, GFP_KERNEL);
        if (!d->regs) return -ENOMEM;
        dev_info(&pdev->dev, "Probed in MOCK mode (no MMIO)\n");
    } else {
        struct resource *res = platform_get_resource(pdev, IORESOURCE_MEM, 0);
        d->regs = devm_ioremap_resource(&pdev->dev, res);
        if (IS_ERR(d->regs)) return PTR_ERR(d->regs);
        dev_info(&pdev->dev, "Probed in REAL mode (MMIO mapped)\n");
    }

    d->misc.minor = MISC_DYNAMIC_MINOR;
    d->misc.name  = "tensor0";
    d->misc.fops  = &tensor_fops;
    d->misc.mode  = device_mode;

    ret = misc_register(&d->misc);
    if (ret) return ret;

    platform_set_drvdata(pdev, d);

    dev_info(&pdev->dev, "Ready: /dev/%s (debug=%d)\n", d->misc.name, debug);
    return 0;
}

#if LINUX_VERSION_CODE >= KERNEL_VERSION(6, 11, 0)
static void tensor_remove(struct platform_device *pdev)
#else
static int tensor_remove(struct platform_device *pdev)
#endif
{
    struct tensor_dev *d = platform_get_drvdata(pdev);
    misc_deregister(&d->misc);
    dev_info(&pdev->dev, "Removed\n");
#if LINUX_VERSION_CODE < KERNEL_VERSION(6, 11, 0)
    return 0;
#endif
}

static const struct of_device_id tensor_of_match[] = {
    { .compatible = "acme,tensor-1.0" },
    {}
};
MODULE_DEVICE_TABLE(of, tensor_of_match);

static struct platform_driver tensor_driver = {
    .probe  = tensor_probe,
    .remove = tensor_remove,
    .driver = {
        .name = "tensor",
        .of_match_table = tensor_of_match,
    }
};

static struct platform_device *tensor_mock_pdev;

static int __init tensor_init(void)
{
    int ret = platform_driver_register(&tensor_driver);
    if (ret)
        return ret;

    if (mock && mock_autocreate) {
        tensor_mock_pdev = platform_device_register_simple("tensor", PLATFORM_DEVID_AUTO, NULL, 0);
        if (IS_ERR(tensor_mock_pdev)) {
            ret = PTR_ERR(tensor_mock_pdev);
            tensor_mock_pdev = NULL;
            platform_driver_unregister(&tensor_driver);
            return ret;
        }
        pr_info("tensor: mock platform device created\n");
    }

    return 0;
}

static void __exit tensor_exit(void)
{
    if (tensor_mock_pdev) {
        platform_device_unregister(tensor_mock_pdev);
        tensor_mock_pdev = NULL;
    }
    platform_driver_unregister(&tensor_driver);
}

module_init(tensor_init);
module_exit(tensor_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("HardMatrix");
MODULE_DESCRIPTION("Hardware Abstraction Layer for Vector Adder Machine");
