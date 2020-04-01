from collections import Counter


class TreeAnnotator:
    def __init__(self, tree):
        self.tree = tree
        self.root = tree.seed_node
        pass

    def annotate_tips(self, annotations):
        for tip in annotations:
            self.annotate_node(tip, annotations[tip])

    def annotate_nodes_from_tips(self, name, acctran):
        self.fitch_parsimony(self.root, name)
        self.reconstruct_ancestors(self.root, [], acctran, name)

    def annotate_node(self, tip_label, annotations):
        filter = lambda taxon: True if taxon.label == tip_label else False
        node = self.tree.find_node_with_taxon(filter)
        if node is None:
            raise KeyError("Taxon %s not found in tree" % tip_label)
        for a in annotations:
            if a != "taxon":
                setattr(node, a, annotations[a])
                node.annotations.add_bound_attribute(a)

    def fitch_parsimony(self, node, name):
        if node.taxon is not None:
            tip_annotation = node.annotations.get_value(name) if node.annotations.get_value(name) is not None else []
            return tip_annotation if isinstance(tip_annotation, list) else [tip_annotation]

        union = set()
        intersection = set()

        for child in node.child_node_iter():
            child_states = self.fitch_parsimony(child, name)
            union = union.union(child_states)
            intersection = set(child_states) if len(intersection) == 0 else intersection.intersection(child_states)

        value = list(intersection) if len(intersection) > 0 else list(union)
        setattr(node, name, value[0] if len(value) == 1 else value)

        node.annotations.add_bound_attribute(name)

        return value

    def reconstruct_ancestors(self, node, parent_states, acctran, name):
        node_states = getattr(node, name) if isinstance(getattr(node, name), list) else [getattr(node, name)]

        if node.taxon is not None and len(node_states) == 1 and node_states[0] is not None:
            assigned_states = node_states
        else:
            assigned_states = list(set(node_states).intersection(parent_states)) if len(
                set(node_states).intersection(parent_states)) > 0 else list(set(node_states).union(parent_states))

        if len(assigned_states) > 1:
            if acctran:
                assigned_states = [state for state in assigned_states if state not in parent_states]
            else:
                # can we delay
                child_states = []
                for child in node.child_node_iter():
                    child_states += getattr(child, name) if isinstance(getattr(child, name), list) else [
                        getattr(child, name)]

                assigned_states = [state for state in assigned_states if
                                   state in parent_states and state in child_states] if len(
                    set(parent_states).intersection(child_states)) > 0 else [state for state in assigned_states if
                                                                             state in child_states]

        setattr(node, name, assigned_states[0] if len(assigned_states) == 1 else assigned_states)

        for child in node.child_node_iter():
            self.reconstruct_ancestors(child, assigned_states, acctran, name)


class AnnotationParser:
    def __init__(self, taxon_key):
        self.taxon_key = taxon_key
        pass

    def get_annotations(self, annotation_list):
        annotation_dict = {}
        for row in annotation_list:
            annotation_dict[row[self.taxon_key]] = row
        return annotation_dict