# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2016 Michele Segata <segata@ccs-labs.org>
#
# Modified by Davide Pedranz <davide.pedranz@gmail.com>

class Packet:
    """
    Class defining a packet to be associated with a transmission event
    """

    # used to create a unique ID for the packet
    __packets_count = 0

    # possible packet states
    # packet currently under reception
    PKT_RECEIVING = 0
    # packet has been correctly received
    PKT_RECEIVED = 1
    # packet has been corrupted due to a collision
    PKT_CORRUPTED = 2
    # packet has been corrupted by the channel during transmission
    PKT_CORRUPTED_BY_CHANNEL = 3

    def __init__(self, size, duration):
        """
        Creates a packet automatically assigning a unique ID to it
        :param size: size of the packet in bytes
        :param duration: packet duration in seconds
        """
        self.size = size
        self.duration = duration
        self.state = Packet.PKT_RECEIVING
        self.id = Packet.__packets_count
        self.prob_correct = 1
        Packet.__packets_count += 1

    def get_id(self):
        """
        Returns packet id
        :returns: id of the packet
        """
        return self.id

    def get_state(self):
        """
        Returns state of a packet
        :returns: state of the packet
        """
        return self.state

    def set_state(self, state):
        """
        Sets packet state.
        :param state: either PKT_RECEIVING, PKT_RECEIVED, or PKT_CORRUPTED
        """
        self.state = state

    def get_size(self):
        """
        Returns packet size
        :returns: packet size in bytes
        """
        return self.size

    def get_duration(self):
        """
        Returns packet duration
        :returns: packet duration in seconds
        """
        return self.duration

    def get_prob_correct(self):
        """
        Return the probability of correct receive this packet if there is no
        collision, according to the "Realistic propagation" model.
        NB: this probability is set by the CHANNEL.
        :return: Probability of correct receiving this packet (if no collisions)
        """
        assert self.prob_correct is not None
        return self.prob_correct

    def set_prob_correct(self, prob_correct):
        """
        Set the probability of correct receive this packet if there is no
        collision. This probability is set by the CHANNEL.
        """
        self.prob_correct = prob_correct

    def dump_packet(self):
        """
        Prints the packet in a human readable format
        """
        if self.state == Packet.PKT_RECEIVING:
            t = "UNDER RECEPTION"
        elif self.state == Packet.PKT_RECEIVED:
            t = "CORRECTLY RECEIVED"
        elif self.state == Packet.PKT_CORRUPTED:
            t = "CORRUPTED"
        print("Packet state: %s\n\n" % t)
