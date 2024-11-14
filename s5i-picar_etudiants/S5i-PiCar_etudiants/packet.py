import struct
def data_to_packet(distance, suiveur):
    suiveurByte = sum(map(lambda x: x[1] << x[0], enumerate(suiveur)))
    print("Byte du suiveur de ligne")
    print(bin(suiveurByte))
    distance = bytearray(struct.pack("f", distance))
    print("Bytes du capteur de distance")
    print(["0x%02x" % b for b in distance])
    distance.append(suiveurByte)
    return distance

# retourne l'angle et la vitesse
def packet_to_data(packet):
    return packet[0], packet[1]