#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>
#include <linux/thermal.h>
#include <linux/mm.h>
#include <net/ip.h>
#include <net/tcp.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Cloud2Edge");
MODULE_DESCRIPTION("Edge sensor telemetry via procfs");
MODULE_VERSION("0.1.0");

#define PROC_NAME "edge_sensor"

static struct proc_dir_entry *proc_entry;

static int read_cpu_temp(void)
{
	struct thermal_zone_device *tz;
	int temp;

	tz = thermal_zone_get_zone_by_name("x86_pkg_temp");
	if (IS_ERR(tz))
		tz = thermal_zone_get_zone_by_name("cpu-thermal");
	if (IS_ERR(tz))
		return -1;
	if (thermal_zone_get_temp(tz, &temp))
		return -1;
	return temp / 1000;
}

static int read_mem_pressure(void)
{
	struct sysinfo si;

	si_meminfo(&si);
	if (si.totalram == 0)
		return -1;
	return 100 - (int)((si.freeram + si.bufferram) * 100 / si.totalram);
}

static long read_tcp_retransmits(void)
{
	return snmp_fold_field(init_net.mib.tcp_statistics,
			       TCP_MIB_RETRANSSEGS);
}

static int edge_sensor_show(struct seq_file *m, void *v)
{
	seq_printf(m, "cpu_temp_c=%d\n", read_cpu_temp());
	seq_printf(m, "mem_pressure_pct=%d\n", read_mem_pressure());
	seq_printf(m, "tcp_retrans_segs=%ld\n", read_tcp_retransmits());

	return 0;
}

static int edge_sensor_open(struct inode *inode, struct file *file)
{
	return single_open(file, edge_sensor_show, NULL);
}

static const struct proc_ops edge_sensor_ops = {
	.proc_open    = edge_sensor_open,
	.proc_read    = seq_read,
	.proc_lseek   = seq_lseek,
	.proc_release = single_release,
};

static int __init edge_sensor_init(void)
{
	proc_entry = proc_create(PROC_NAME, 0444, NULL, &edge_sensor_ops);
	if (!proc_entry) {
		pr_err("edge_sensor: failed to create /proc/%s\n", PROC_NAME);
		return -ENOMEM;
	}
	pr_info("edge_sensor: module loaded, /proc/%s created\n", PROC_NAME);
	return 0;
}

static void __exit edge_sensor_exit(void)
{
	proc_remove(proc_entry);
	pr_info("edge_sensor: module unloaded, /proc/%s removed\n", PROC_NAME);
}

module_init(edge_sensor_init);
module_exit(edge_sensor_exit);
