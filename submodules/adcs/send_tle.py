def send_tle(pry_packet, abs_packet, mag_packet):
 pitch = pry_packet['pitch']
 roll = pry_packet['roll']
 yaw = pry_packet['yaw']
  
 abs_x = abs_packet['X']
 abs_y = abs_packet['Y']
 abs_z = abs_packet['Z']
  
 mag_x = mag_packet['X']
 mag_y = mag_packet['Y']
 mag_z = mag_packet['Z']

 t = datetime.utcnow()
 t = t.timestamp()

 packet = "A"
 packet += base64.b64encode(struct.pack('d', t)).decode("UTF-8")
 packet += base64.b64encode(struct.pack('fff', float(pitch),
                                        float(roll), float(yaw))).decode("UTF-8")
 packet += base64.b64encode(struct.pack('fff', float(abs_x),
                                        float(abs_y), float(abs_z))).decode("UTF-8")
 packet += base64.b64encode(struct.pack('fff', float(mag_x),
                                        float(mag_y), float(mag_z))).decode("UTF-8")
 # print(packet)
 telemetry.enqueue_submodule_packet(packet)
