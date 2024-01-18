import sys
from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
import cmd2
import re

import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from swap import swap


class FirewallController(cmd2.Cmd):
    prompt = 'Firewall_CLI> '

    def __init__(self, sw_name):
        super().__init__()  # Call the cmd2.Cmd __init__ method
        self.topo = load_topo('topology.json')
        self.sw_name = sw_name
        self.thrift_port = self.topo.get_thrift_port(sw_name)
        self.controller = SimpleSwitchThriftAPI(self.thrift_port)
        self.controller = swap(self.sw_name, 'firewall')

    def see_filters(self):
        nb_entries = self.controller.table_num_entries('fw')
        if nb_entries == 0:
            print("No rule")
            print("\u200B")
            return
        # print(str(self.controller.table_dump('fw')))
        for i in range(0,nb_entries):
            print("\nRule " + str(i) + " : ")
            print(str(self.controller.table_dump_entry('fw', i)))
            self.controller.counter_read('rule_counter', i)
        print("\u200B")

    def see_load(self):
        print("Total counter: ")
        self.controller.counter_read('count_in', 0)
        print("\u200B")

    def add_fw_rule(self, flow):
        self.controller.table_add("fw", "drop", flow, [])
        print("Rule : drop " + str(flow) + " added")
        print("\u200B")
    
    # cmd2 methods
    def do_see(self, args):
        if args == 'filters':
            self.see_filters()
        elif args == 'load':
            self.see_load()

    def do_add_fw_rule(self, args):
        self.add_fw_rule(args.split())


def matches_regex(string, regex):
    return re.match(regex, string) is not None

if __name__ == '__main__':
    if matches_regex(sys.argv[1], r's[0-9]+$'):
        app = FirewallController(sys.argv[1])
        app.cmdloop()
