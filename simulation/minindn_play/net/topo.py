from mininet.net import Mininet
from mininet.log import info, error
from mininet.link import Link

class TopoExecutor:
    def __init__(self, net: Mininet):
        self.net = net

    async def get_topo(self):
        """UI Function: Get topology"""
        nodes = []
        nodeIds = set()
        links = []

        for host in self.net.hosts:
            nodes.append(self._node_dict(host))
            nodeIds.add(host.name)

        for switch in self.net.switches:
            nodes.append(self._node_dict(switch, switch=True))

        for station in getattr(self.net, 'stations', []):
            if station.name not in nodeIds:
                nodes.append(self._node_dict(station))

        for link in self.net.links:
            if obj := self._link_dict(link):
                links.append(obj)

        return {
            'nodes': nodes,
            'links': links,
        }

    async def add_link(self, a, b, id, opts):
        """UI Function: Add link"""
        link = self.net.addLink(self.net[a], self.net[b], **self._conv_link_opts(opts))
        info('Added link {}\n'.format(link))
        return {
            'id': id,
            'mnId': str(link),
            **opts,
        }

    async def del_link(self, a, b, mnId):
        """UI Function: Delete link"""
        link = self._get_link(a, b, mnId)
        if link:
            self.net.delLink(link)
            return True

        error('No link found to remove for {}\n'.format(mnId))
        return False

    async def upd_link(self, a, b, mnId, opts):
        """UI Function: Update link"""
        link = self._get_link(a, b, mnId)
        if link:
            params = self._conv_link_opts(opts)
            link.intf1.config(**params)
            link.intf2.config(**params)
            for p in params:
                link.intf1.params[p] = params[p]
                link.intf2.params[p] = params[p]
            return True

        info('No link to configure for {}\n'.format(mnId))
        return False

    async def add_node(self, id, label):
        """UI Function: Add node (host is added)"""
        self.net.addHost(label)
        return {
            'id': id,
            'label': label,
        }

    async def del_node(self, id):
        """UI Function: Delete node"""
        self.net.delNode(self.net[id])
        info('Removed node {}\n'.format(id))
        return True

    async def set_node_pos(self, id, x, y):
        """UI Function: Set node position"""
        node = self.net[id]
        if not node or not hasattr(node, 'position'):
            return False
        x, y = x / 10, y / 10
        z = node.position[2] if len(node.position) > 2 else 0
        node.setPosition("%d,%d,%d" % (x, y, z))
        info('Set position of {} to {},{}\n'.format(id, x, y))
        return True

    def _node_dict(self, node, switch=False):
        val = {
            'id': node.name,
            'label': node.name,
        }

        if switch:
            val['isSwitch'] = True

        if hasattr(node, 'position'):
            # Mininet positions are in m, NDN-Play are much smaller
            val['x'] = node.position[0] * 10
            val['y'] = node.position[1] * 10

        if hasattr(node, 'params') and 'params' in node.params:
            p = node.params['params']
            if 'color' in p:
                val['color'] = p['color']

        return val

    def _link_dict(self, link):
        if isinstance(link.intf2, str):
            if link.intf2 == 'wifiAdhoc':
                # TODO: visualize adhoc links
                pass
            return None

        obj = {
            'mnId': str(link),
            'from': link.intf1.node.name,
            'to': link.intf2.node.name,
        }

        if 'delay' in link.intf1.params:
            d1 = int(link.intf1.params['delay'][:-len('ms')])
            d2 = int(link.intf2.params['delay'][:-len('ms')])
            obj['latency'] = (d1 + d2) / 2

        if 'loss' in link.intf1.params:
            l1 = link.intf1.params['loss']
            l2 = link.intf2.params['loss']
            obj['loss'] = (l1 + l2) / 2

        return obj

    def _get_link(self, a, b, mnId):
        """Helper: get link between two nodes by name"""
        for link in self.net.linksBetween(self.net[a], self.net[b]):
            if str(link) == mnId:
                return link

        return None

    def _conv_link_opts(self, opts: dict):
        """Helper: convert link options"""
        params = {}
        if 'latency' in opts and opts['latency'] is not None and int(opts['latency']) >= 0:
            params['delay'] = str(int(opts['latency'])) + 'ms'
        if 'loss' in opts and opts['loss'] is not None and float(opts['loss']) >= 0:
            params['loss'] = float(opts['loss'])
        return params
