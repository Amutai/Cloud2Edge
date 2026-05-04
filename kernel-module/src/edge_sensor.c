#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Cloud2Edge");
MODULE_DESCRIPTION("Edge sensor telemetry via procfs");
MODULE_VERSION("0.1.0");

static int __init edge_sensor_init(void)
{
	pr_info("edge_sensor: module loaded\n");
	return 0;
}

static void __exit edge_sensor_exit(void)
{
	pr_info("edge_sensor: module unloaded\n");
}

module_init(edge_sensor_init);
module_exit(edge_sensor_exit);
