import ujson as json
from collections import defaultdict

class FineGrainedUtil(object):
    def __init__(self, hierarchy_dir):
        super(FineGrainedUtil, self).__init__()
        # self.hierarchy_dir = hierarchy_dir
        self.child_parents_dict = self.load_parent(hierarchy_dir)

    def print_hierarchy(self, hierarchy_dir):
        types_total = set()
        types_already = set()
        child_parent_dict = {}  # 1-1 mapping
        parent_child_dict = json.load(open(hierarchy_dir))
        for parent in parent_child_dict:
            for child in parent_child_dict[parent]:
                child_parent_dict[child] = parent
        for type_1 in parent_child_dict:
            types_total.add(type_1)
            if (type_1 not in child_parent_dict) or (child_parent_dict[type_1] == []) or (len(child_parent_dict[type_1]) == 0):
                print(type_1)
                types_already.add(type_1)
                for type_2 in parent_child_dict[type_1]:
                    if type_2 in types_already:
                        continue
                    print('\t', type_2)
                    types_already.add(type_2)
                    for type_3 in parent_child_dict[type_2]:
                        if type_3 in types_already:
                            continue
                        print('\t\t', type_3)
                        types_already.add(type_3)
                        for type_4 in parent_child_dict[type_3]:
                            if type_4 in types_already:
                                continue
                            print('\t\t\t', type_4)
                            types_already.add(type_4)
                            for type_5 in parent_child_dict[type_4]:
                                if type_5 in types_already:
                                    continue
                                print('\t\t\t\t', type_5)
                                types_already.add(type_5)
                                for type_6 in parent_child_dict[type_5]:
                                    if type_6 in types_already:
                                        continue
                                    print('\t\t\t\t\t', type_6)
                                    types_already.add(type_6)
                                    for type_7 in parent_child_dict[type_6]:
                                        if type_7 in types_already:
                                            continue
                                        print('\t\t\t\t\t\t', type_7)
                                        types_already.add(type_7)
                                        for type_8 in parent_child_dict[type_7]:
                                            if type_8 in types_already:
                                                continue
                                            print('\t\t\t\t\t\t\t', type_8)
                                            types_already.add(type_8)
                                            for type_9 in parent_child_dict[type_8]:
                                                if type_9 in types_already:
                                                    continue
                                                print('\t\t\t\t\t\t\t\t', type_9)
                                                types_already.add(type_9)
                                                for type_10 in parent_child_dict[type_8]:
                                                    if type_10 in types_already:
                                                        continue
                                                    print('\t\t\t\t\t\t\t\t\t', type_10)
                                                    types_already.add(type_10)
                                                    for type_11 in parent_child_dict[type_10]:
                                                        if type_11 in types_already:
                                                            continue
                                                        print('\t\t\t\t\t\t\t\t\t\t', type_11)
                                                        types_already.add(type_11)
                                                        for type_12 in parent_child_dict[type_11]:
                                                            if type_12 in types_already:
                                                                continue
                                                            print('\t\t\t\t\t\t\t\t\t\t\t', type_12)
                                                            types_already.add(type_12)
                                                            for type_13 in parent_child_dict[type_11]:
                                                                if type_13 in types_already:
                                                                    continue
                                                                print('\t\t\t\t\t\t\t\t\t\t\t\t', type_13)
                                                                types_already.add(type_13)
                                                                for type_14 in parent_child_dict[type_13]:
                                                                    if type_14 in types_already:
                                                                        continue
                                                                    print('\t\t\t\t\t\t\t\t\t\t\t\t\t', type_14)
                                                                    types_already.add(type_14)
                                                                    for type_15 in parent_child_dict[type_14]:
                                                                        if type_15 in types_already:
                                                                            continue
                                                                        print('\t\t\t\t\t\t\t\t\t\t\t\t\t\t', type_15)
                                                                        types_already.add(type_15)
                                                                        for type_16 in parent_child_dict[type_15]:
                                                                            if type_16 in types_already:
                                                                                continue
                                                                            print('\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t', type_16)
                                                                            types_already.add(type_16)
                                                                            for type_17 in parent_child_dict[type_16]:
                                                                                if type_17 in types_already:
                                                                                    continue
                                                                                print('\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t', type_17)
                                                                                types_already.add(type_17)
                                                                                for type_18 in parent_child_dict[
                                                                                    type_17]:
                                                                                    if type_18 in types_already:
                                                                                        continue
                                                                                    print(
                                                                                        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t',
                                                                                        type_18)
                                                                                    types_already.add(type_18)
                                                                                    for type_19 in parent_child_dict[
                                                                                        type_18]:
                                                                                        if type_19 in types_already:
                                                                                            continue
                                                                                        print(
                                                                                            '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t',
                                                                                            type_19)
                                                                                        types_already.add(type_19)
        total_num = len(types_total)
        print('total_num', total_num)


    def load_parent(self, hierarchy_dir):
        child_parent_dict = {} # 1-1 mapping
        parent_child_dict = json.load(open(hierarchy_dir))
        for parent in parent_child_dict:
            for child in parent_child_dict[parent]:
                child_parent_dict[child] = parent

        child_parents_dict = {}
        # child_parents_dict = defaultdict(list)
        for child in child_parent_dict:
            child_parents_dict[child] = []
            self._get_parents(child, child_parent_dict, child_parents_dict[child])

        return child_parents_dict

    def _get_parents(self, child, child_parent_dict, parents):
        if child not in child_parent_dict:
            return parents
        else:
            parent_type = child_parent_dict[child]
            parents.append(parent_type)
            self._get_parents(parent_type, child_parent_dict, parents)

    def get_all_types(self, type_list):
        alltypes = set()
        for type in type_list:
            alltypes.add(type)
            if type in self.child_parents_dict:
                alltypes.update(self.child_parents_dict[type])
        return list(alltypes)

    def _prep_type_old(self, typestr):
        return typestr.replace("https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#", "")

    # <entityid, fine_type_list>
    def entity_finegrain_by_json(self, entity_finegrain_json, entity_freebase_tab, entity_coarse,
                                 filler_coarse=None, add_coarse=True, add_parent=True):
        entity_dict = defaultdict(set)
        fine_mapping = json.load(open(entity_finegrain_json))
        offset_fb_mapping = self._load_offset_fine_mapping(entity_freebase_tab)
        self._entity_finegrain_by_json(offset_fb_mapping, fine_mapping, entity_dict, entity_coarse,
                                  add_coarse, add_parent)
        if filler_coarse is not None and len(filler_coarse) != 0:
            self._entity_finegrain_by_json(offset_fb_mapping, fine_mapping, entity_dict, filler_coarse,
                                      add_coarse, add_parent)
        return entity_dict

    def _entity_finegrain_by_json(self, offset_fb_mapping, fb_fine_mapping, entity_dict, coarse_file,
                                  add_coarse=True, add_parent=True):
        for line in open(coarse_file):
            if line.startswith(':Entity') or line.startswith(':Filler'):  # (????)
                line = line.rstrip('\n')
                tabs = line.split('\t')
                # if tabs[0] not in entity_dict:
                #     entity_dict[tabs[0]] = set()#[]
                if tabs[1] == 'type':
                    if add_coarse:
                        type_str = self._prep_type_old(tabs[2])
                        entity_dict[tabs[0]].add(type_str)#append(type_str)
                elif 'mention' in tabs[1]:
                    offset = tabs[3]
                    if offset in offset_fb_mapping:
                        link = offset_fb_mapping[offset]
                        if link in fb_fine_mapping:
                            fine_type = fb_fine_mapping[link]
                            # print(fine_type)
                            if add_parent:
                                entity_dict[tabs[0]].update(self.get_all_types(fine_type)) #.extend(self.get_all_types(fine_type))
                            else:
                                entity_dict[tabs[0]].update(fine_type)#.extend(fine_type)
                # if tabs[1] == 'link':
                #     link = tabs[2].replace("LDC2015E42:", "")
                #     if link in fb_fine_mapping:
                #         entity_dict[tabs[0]].extend(self.get_all_types(fb_fine_mapping[link]))
                #         # entity_dict[tabs[0]].extend(fine_mapping[link])

    def _load_offset_fine_mapping(self, entity_coarse_freebase):
        offset_fine_mapping = {}
        for line in open(entity_coarse_freebase):
            line = line.rstrip('\n')
            tabs = line.split('\t')
            offset = tabs[3]
            link = tabs[4]
            if not link.startswith('NIL'):
                offset_fine_mapping[offset] = link
        return offset_fine_mapping


# if __name__ == '__main__':
#     hierarchy_dir = 'yago_taxonomy_wordnet_single_parent.json'
#     finetype_util = FineGrainedUtil(hierarchy_dir)
#
#     # type_list = ["Capital108518505", "BusinessDistrict108539072"]
#     # type_list = ["Person100007846"]
#     # print(finetype_util.get_all_types(type_list))
#     finetype_util.print_hierarchy(hierarchy_dir)