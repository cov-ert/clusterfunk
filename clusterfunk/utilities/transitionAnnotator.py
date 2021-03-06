import dendropy

from clusterfunk.utilities.utils import SafeNodeAnnotator

nodeAnnotator = SafeNodeAnnotator(safe=True)


class TransitionAnnotator:
    def __init__(self, trait, include_parent, transition_name, transition_suffix="", include_root=False,
                 stubborn=False):

        self.trait = trait
        self.From = None
        self.to = None
        self.count = 0
        self.transition_points = []
        self.include_parent = include_parent
        self.found_transition = False
        self.transition_suffix = transition_suffix
        self.include_root = include_root
        self.stubborn = stubborn

        self.transition_name = transition_name

    def annotate_transitions(self, tree, From=None, to=None):

        if From is None and to is None:
            raise ValueError("Must provide at least a from or to state")

        if From is not None and self.stubborn:
            raise ValueError("stubborn not implemented for use with from")
        self.From = From
        self.to = to
        self.count = 0
        self.transition_points = []
        node = tree.seed_node
        self.traverse(node)
        return self.count

    def traverse(self, node):
        node_state = node.annotations.get_value(self.trait)
        parent_state = node.parent_node.annotations.get_value(self.trait) if node.parent_node != None else None


        if parent_state is not None:
            if self.From is not None:
                if parent_state == self.From:
                    if self.to is not None:
                        if node_state == self.to:
                            self.transition_points.append(node)
                            self.count += 1
                            nodeAnnotator.annotate(node, self.transition_name, self.transition_suffix + str(self.count))
                    elif node_state != parent_state:
                        self.transition_points.append(node)
                        self.count += 1
                        nodeAnnotator.annotate(node, self.transition_name, self.transition_suffix + str(self.count))

                else:
                    if node_state != self.From:
                        if node.parent_node.annotations.get_value(self.transition_name) is not None:
                            nodeAnnotator.annotate(node, self.transition_name,
                                                   node.parent_node.annotations.get_value(self.transition_name))
            else:
                if self.stubborn:
                    if node.parent_node.annotations.get_value(self.transition_name) is not None:
                        #In a transition
                        if node.is_leaf():
                            if node_state == self.to:
                                nodeAnnotator.annotate(node, self.transition_name,
                                                       node.parent_node.annotations.get_value(self.transition_name))
                        else:
                            nodeAnnotator.annotate(node, self.transition_name,
                                               node.parent_node.annotations.get_value(self.transition_name))
                    else:
                        if node_state == self.to:
                            if parent_state == self.to:
                                nodeAnnotator.annotate(node, self.transition_name,
                                                       node.parent_node.annotations.get_value(self.transition_name))
                            else:
                                self.transition_points.append(node)
                                self.count += 1
                                nodeAnnotator.annotate(node, self.transition_name, self.transition_suffix + str(self.count))
                else:
                    if node_state == self.to:
                        if parent_state == self.to:
                            nodeAnnotator.annotate(node, self.transition_name,
                                                   node.parent_node.annotations.get_value(self.transition_name))
                        else:
                            self.transition_points.append(node)
                            self.count += 1
                            nodeAnnotator.annotate(node, self.transition_name, self.transition_suffix + str(self.count))


        else:
            if self.to is not None:
                if self.include_root:
                    if node_state == self.to:
                        self.transition_points.append(node)
                        self.count += 1
                        nodeAnnotator.annotate(node, self.transition_name, self.transition_suffix + str(self.count))

        for child in node.child_node_iter():
            self.traverse(child)

    def split_at_transitions(self, tree, From=None, to=None):
        self.annotate_transitions(tree, From, to)
        trees = []
        for node in self.transition_points:
            new_root = node
            if self.include_parent:
                if node.parent_node is not None:
                    new_root = node.parent_node
            trees.append(
                    {"id": node.annotations.get_value(self.transition_name), "tree": dendropy.Tree(seed_node=new_root)})
        return trees
