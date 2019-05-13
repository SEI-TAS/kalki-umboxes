
import uuid
import os
import os.path
import logging
import sys
import random
from argparse import ArgumentParser


import vm.vmutils as vmutils
import vm.vm_descriptor as vm_descriptor
import vm.diskimage


MAX_INSTANCES = 1000
NUM_SEPARATOR = "-"
XML_VM_TEMPLATE = "ovs-umbox-manager/vm/vm_template.xml"

# Base names for the TUN/TAP virtual interfaces on the data node that handle the VM interfaces.
CONTROL_TUN_PREFIX = "vnucont"
DATA_TUN_PREFIX = "vnudata"

# Path to stored VM umbox images in data node.
DATA_NODE_IMAGES_PATH = "/home/kalki/images/"
INSTANCES_FOLDER = "instances"

# Global logger.
logger = None


def setup_custom_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    #handler = logging.FileHandler(file_path, mode='w')
    #handler.setFormatter(formatter)
    #logger.addHandler(handler)

    screen_handler = logging.StreamHandler(stream=sys.stderr)
    screen_handler.setFormatter(formatter)
    logger.addHandler(screen_handler)
    return logger


def create_and_start_umbox(data_node_ip, umbox_id, image_name, image_path, control_bridge, data_bridge):
    umbox = VmUmbox(umbox_id, image_name, image_path, control_bridge, data_bridge)
    #umbox.create_linked_image()
    umbox.start(data_node_ip)
    logger.info("Umbox started.")

    return umbox


def stop_umbox(data_node_ip, umbox_id, image_name):
    """Stops a running instance of an umbox."""
    umbox = VmUmbox(umbox_id, image_name)
    umbox.stop(data_node_ip)
    logger.info("Umbox stopped.")


def generate_mac(instance_id):
    """Generate a mac from the instance id. We are using te 00163e prefix used by Xensource."""
    mac = [
        0x00, 0x16, 0x3e,
        random.randint(0x00, 0x7f),
        int(instance_id) // MAX_INSTANCES,
        int(instance_id) % 100
    ]
    return ':'.join(map(lambda x: "%02x" % x, mac))


class VmUmbox(object):
    """Class that stores information about a VM that is working as a umbox."""

    def __init__(self, umbox_id, image_name, image_path=None, control_bridge=None, data_bridge=None):
        """Default constructor."""
        self.umbox_id = umbox_id
        self.image_name = image_name
        self.instance_name = image_name + NUM_SEPARATOR + self.umbox_id

        self.image_path = image_path
        self.control_bridge = control_bridge
        self.data_bridge = data_bridge
        self.control_iface_name = CONTROL_TUN_PREFIX + self.umbox_id
        self.data_iface_name = DATA_TUN_PREFIX + self.umbox_id

        # Only to be used for newly started VMs.
        self.control_mac_address = generate_mac(self.umbox_id)
        self.data_mac_address = generate_mac(self.umbox_id)

        #self.instance_disk_path = os.path.join(DATA_NODE_IMAGES_PATH, INSTANCES_FOLDER, self.instance_name)

        logger.info("VM name: " + self.instance_name)

    #def create_linked_image(self):
    #    """Create a linked qcow2 file so that we don't modify the template, and we don't have to copy the complete image."""
        # TODO: find way to do this remotely.
        #template_image = vm.diskimage.DiskImage(self.image_path)
        #template_image.create_linked_qcow2_image(self.instance_disk_path)

    def get_updated_descriptor(self, xml_descriptor_string):
        """Updates an XML containing the description of the VM with the current info of this VM."""

        # Get the descriptor and inflate it to something we can work with.
        xml_descriptor = vm_descriptor.VirtualMachineDescriptor(xml_descriptor_string)

        xml_descriptor.set_uuid(str(uuid.uuid4()))
        xml_descriptor.set_name(self.instance_name)

        # TODO: change this back to instance_disk_path when we are able to create it.
        xml_descriptor.set_disk_image(self.image_path, 'qcow2')

        logger.info('Adding OVS connected network interface, using tap: ' + self.data_iface_name)
        xml_descriptor.add_bridge_interface(self.data_bridge, self.data_mac_address, target=self.data_iface_name, ovs=True)

        logger.info('Adding control plane network interface, using tap: ' + self.control_iface_name)
        xml_descriptor.add_bridge_interface(self.control_bridge, self.control_mac_address, target=self.control_iface_name)

        # Remove seclabel item, which tends to generate issues when the VM is executed.
        xml_descriptor.remove_sec_label()

        updated_xml_descriptor_string = xml_descriptor.get_as_string()
        return updated_xml_descriptor_string

    def _connect_to_remote_hypervisor(self, hypervisor_host_ip):
        """Explicitly connect to hypervisor to ensure we are getting to remote libvirtd."""
        vmutils.VirtualMachine.get_hypervisor_instance(is_system_level=True, host_name=hypervisor_host_ip, transport='tcp')

    def start(self, hypervisor_host_ip):
        """Creates a new VM using the XML template plus the information set up for this umbox."""
        self._connect_to_remote_hypervisor(hypervisor_host_ip)

        # Set up VM information from template and umbox data.
        template_xml_file = os.path.abspath(XML_VM_TEMPLATE)
        with open(template_xml_file, 'r') as xml_file:
            template_xml = xml_file.read().replace('\n', '')
        updated_xml = self.get_updated_descriptor(template_xml)
        logger.info(updated_xml)

        # Check if the VM is already running.
        vm = vmutils.VirtualMachine()
        try:
            # If it is, connect and destroy it, before starting a new one.
            vm.connect_to_virtual_machine_by_name(self.instance_name)
            logger.info("VM with same name was already running; destroying it.")
            vm.destroy()
            logger.info("VM destroyed.")
        except vmutils.VirtualMachineException, ex:
            logger.warning("VM was not running.")
            vm = vmutils.VirtualMachine()

        # Then create and start the VM itself.
        logger.info("Starting new VM.")
        vm.create_and_start_vm(updated_xml)
        logger.info("New VM started.")

    def pause(self, hypervisor_host_ip):
        self._connect_to_remote_hypervisor(hypervisor_host_ip)
        vm = vmutils.VirtualMachine()
        try:
            vm.connect_to_virtual_machine_by_name(self.instance_name)
            vm.pause()
        except:
            logger.error("VM not found.")

    def unpause(self, hypervisor_host_ip):
        self._connect_to_remote_hypervisor(hypervisor_host_ip)
        vm = vmutils.VirtualMachine()
        try:
            vm.connect_to_virtual_machine_by_name(self.instance_name)
            vm.unpause()
        except:
            logger.error("VM not found.")

    def stop(self, hypervisor_host_ip):
        self._connect_to_remote_hypervisor(hypervisor_host_ip)
        vm = vmutils.VirtualMachine()
        try:
            vm.connect_to_virtual_machine_by_name(self.instance_name)
            vm.destroy()

            #TODO: destroy instance image file.
        except:
            logger.warning("VM not found.")


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument("-c", "--command", dest="command", required=True, help="Command: start or stop")
    parser.add_argument("-s", "--server", dest="datanodeip", required=True, help="IP of the data node server")
    parser.add_argument("-u", "--umbox", dest="umboxid", required=False, help="id of the umbox instance")
    parser.add_argument("-i", "--image", dest="imagename", required=False, help="name of the umbox image")
    parser.add_argument("-p", "--imagepath", dest="imagepath", required=False, help="the path to the image file")
    parser.add_argument("-bc", "--bridgecontrol", dest="controlbr", required=False, help="name of the control virtual bridge")
    parser.add_argument("-bd", "--bridgedata", dest="databr", required=False, help="name of the data ovs virtual bridge")
    args = parser.parse_args()
    return args


def main():
    global logger
    logger = setup_custom_logger("main")

    args = parse_arguments()
    logger.info("Command: " + args.command)
    logger.info("Data node to use: " + args.datanodeip)
    if args.command == "start":
        logger.info("Umbox ID: " + args.umboxid)
        logger.info("Image name: " + args.imagename)
        logger.info("Image path: " + args.imagepath)
        logger.info("Control bridge: " + args.controlbr)
        logger.info("Data bridge: " + args.databr)

        umbox = create_and_start_umbox(args.datanodeip, args.umboxid, args.imagename, args.imagepath, args.controlbr, args.databr)

        # Print the TAP device name so that it can be returned and used by ovs commands if needed.
        print(umbox.data_iface_name)
    else:
        logger.info("Instance: " + args.imagename + "-" + args.umboxid)

        stop_umbox(args.datanodeip, args.umboxid, args.imagename)


if __name__ == '__main__':
    main()
