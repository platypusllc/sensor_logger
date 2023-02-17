#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix

import time
import json
import datetime

from .AtlasI2C import AtlasI2C

class AtlasLogger(Node):
	def __init__(self):
		super().__init__('AtlasLogger')

		self._devices = self._get_devices()

		# Create new logfile name
		curr_time = datetime.datetime.now()
		self._logfile_name = f"/home/usv/logs/{curr_time.isoformat(sep='_').split('.')[0]}_atlas.jsonl"

		# Subscribe to new GPS updates
		self._gps_sub = self.create_subscription(NavSatFix, '/mavros/global_position/global', self._gps_callback, 10)
		self._last_gps = [0., 0.]

		sensor_rate = 1 # Hz
		self.create_timer(1./sensor_rate, self._sensor_loop)

	def _get_devices(self):
		device = AtlasI2C()
		device_address_list = device.list_i2c_devices()
		device_list = []

		for i in device_address_list:
			device.set_i2c_address(i)
			response = device.query("i")
			
			# check if the device is an EZO device
			checkEzo = response.split(",")
			if len(checkEzo) > 0:
				if checkEzo[0].endswith("?I"):
					# yes - this is an EZO device
					moduletype = checkEzo[1]
					response = device.query("name,?").split(",")[1]
					device_list.append(AtlasI2C(address = i, moduletype = moduletype, name = response))
		return device_list

	def _gps_callback(self, msg):
		self._last_gps = [msg.latitude, msg.longitude]

	def _sensor_loop(self):
		for dev in self._devices:
			dev.write('r')

		reading_time = datetime.datetime.now()
		# figure out how long to wait before reading the response
		timeout = self._devices[0].get_command_timeout('r')
		# if we dont have a timeout, dont try to read, since it means we issued a sleep command

		reading_dicts = []
		if(timeout):
			time.sleep(timeout)
			for dev in self._devices:
				reading = dev.read().split(':')
				if reading[0].upper().startswith('SUCCESS'):
					reading_dicts.append({'time':reading_time.timestamp(), 'location':self._last_gps, 'sensor':reading[1], 'data':reading[2]})
		
		with open(self._logfile_name, 'a+') as log:
			for d in reading_dicts:
				json.dump(d, log)
				log.write('\n')


def main(args=None):
	rclpy.init(args=args)
	node = AtlasLogger()
	rclpy.spin(node)
	node.destroy_node()
	rclpy.shutdown()

if __name__=='__main__':
	main()