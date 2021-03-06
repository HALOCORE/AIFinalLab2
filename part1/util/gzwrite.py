class GzDigraphWriter:
    """
    graphviz代码生成
    """
    def __init__(self, name):
        self.name = name
        self.__code_list = list()
        self.__code_list.append("digraph " + name + "{")
        self.__code_list.append("ordering = out;")

    def add_edge(self, name1, name2, label="", color="black"):
        """在digraph上添加边"""
        attrs = list()
        if label != "":
            attrs.append('label="%s"' % label)
        if color != 'black':
            attrs.append("color=%s" % color)
        if len(attrs) > 0:
            attr_code = "[%s]" %(','.join(attrs))
        else:
            attr_code = ""
        self.__code_list.append(str(name1) + " -> " + str(name2) + attr_code + ";")

    def set_node(self, name, color=None, label=None, shape=None):
        """在digraph中设置节点颜色和label"""
        attr_list = list()
        color_code = "" if not color else "color=" + color
        label_code = "" if not label else "label=\"" + label + "\""
        shape_code = "" if not shape else "shape=" + shape
        attr_list.append(color_code)
        attr_list.append(label_code)
        attr_list.append(shape_code)
        attr_list = [attr for attr in attr_list if attr != ""]
        code = ", ".join(attr_list)
        code = " [" + code + "]" if code != "" else ""
        code = str(name) + code + ";"
        self.__code_list.append(code)

    def get_codes(self):
        """获取代码"""
        return self.__code_list + ["}"]



