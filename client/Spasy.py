from SpasyTree import *
from pympler import asizeof
from random import randint, seed
from pprint import pprint

class Spasy:
    """
    Spatial Sync (SPASY) is a Named Data Networking (NDN) Sync protocol meant for 
    use in augmented reality environments (and eventually the Metaverse). 

    Uses a SpasyTree to identify where all digital assets are within a given
    area and maintain synchronization of assets between users.

    Assumes SpasyTree root is at Geohash Level 6 and data is stored in leaves
    at Geohash Level 10.
    """

    def __init__(self, geocode: str, max_updates: int=50) -> None:
        
        #self._tree = SpasyTree(9, Node(geocode))
        self._trees = {str(geocode): SpasyTree(9, max_updates, Node(geocode))}
        self._subscribed_trees = [geocode]

    ######### ACCESSORS #########
    @property
    def trees(self) -> SpasyTree:
        """Get or set the data SpasyTree data structure."""
        return self._trees
    
    @property
    def subscribed_trees(self) -> set:
        """Get or set the subscribed trees."""
        return self._subscribed_trees


    def build_tree(self, size: int=0) -> None:
        """Insert elements into the tree to automate the building of trees.

        Args:
            size (int, optional): the number of names to insert in the tree. 
                                  Defaults to 0.
        """
        # get the string value of the root's geocode
        tree_geocode = ''.join(self._tree.root.geocode)
        # generate a name with a geocode and insert it in the tree
        seed_value = 0 # we want the tree to always be the same for experiments
        for i in range(size):
            
            name = self._generate_name(seed_value) + self._generate_geocode(seed_value, tree_geocode)
            #print(f'Name being inserted: {name}')
            self._tree.insert(name)
            insert_info = (time.time(), 'i', name)
            self._add_to_recent_updates(insert_info)
            seed_value += 1000 # increment the seed to make sure it doesn't generate the same string and geocode
                               # multiple times for the same tree
            #print(f'\n######### RECENT UPDATES #########\n')
            #pprint(self._recent_updates)

    def build_tree_from_file(self, geocode: str, filename: str, size: int, timestamp: bool=False) -> None:
        """
        Build a tree from a file that contains names and, optionally, timestamps.

        Args:
            filename (str): the name of the file that stores the names to be added to the tree.
            size (int): the size of the tree once built.
            timestamp (bool, optional): True, if there is a timestamp associated with the named data 
                                        in the file.
                                        False otherwise. Defaults to False.
        """

        if not timestamp:
            with open(filename, 'r') as file:
                count = 0
                while count <= size:
                    #print(f'GEOCODE: {geocode}')
                    self.add_data_to_tree(geocode, file.readline().strip())
                    count += 1

        else:
            with open(filename, 'r') as file:
                count = 0
                while count <= size:
                    line = file.readline().strip().split(',')
                    # print(f'LINE: {line}')
                    #print(f'GEOCODE: {geocode}') 
                    # if the line is empty, we've reached the end of the file
                    if line == ['']:
                        break
                    #split_line = line.split(',')
                    named_data = line[0]
                    time_added = line[1]
                    #print(f'Named data: {named_data}')
                    #print(f'Timestamp: {time_added}')
                    self.add_data_to_tree(geocode, named_data, time_added)
                    count += 1

    def _create_experiment_tree(self, size: int, max_length_name: int, timestamp: bool=False) -> None:
        """
        Create a file that builds randomly named data strings to be used to build a
        SpasyTree that will have the same data. Used to run consistent experiments.

        Args:
            size (int): The number of elements that the tree will have.
            max_length_name (int): The maximum length of the hierarchical name of the named data.
            timestamp (bool): Will add a timestamp for each name to allow for trees to match when running experiments, if True.
                              Defaults to False.
        """
        word_list = []
        with open('client/words.txt') as file:
            for word in file:
                word_list.append(word.strip())

        name_list = []
        
        for i in range(size):
            name = ""
            number_elements = randint(2, max_length_name) # determine the number of elements in the named data string
        # generate the hierarchical name
            for j in range(number_elements):
                name = name + '/' + word_list[randint(0,len(word_list)-1)]

            # if the length of the string is even, add a version number between 1 and 10
            if number_elements % 2 == 0:
                version_number = '_v' + str(randint(1,10))
                name = name + '/' + version_number

            # create a divider to accommodate the geocode
            name = name + '/'

            insert_geocode =  ''.join(self._tree.root.geocode)
            valid_characters = '0123456789bcdefghjkmnpqrstuvwxyz'

            max_geocode_length = self.tree.max_depth
            while len(insert_geocode) <= max_geocode_length:
                
                insert_geocode = insert_geocode + valid_characters[randint(0, len(valid_characters) - 1)]

            
            name_list.append(name + insert_geocode)
        
        if timestamp:
            with open('spasy_tree.txt', 'w') as file2:
                for entry in name_list:
                    time_added = str(time.time())
                    string_to_add = entry + ',' + time_added + '\n'
                    file2.write(entry + ',' + time_added + '\n')
        else:
            with open('spasy_tree.txt', 'w') as file2:
                for entry in name_list:
                    file2.write(entry)
            

    def _generate_name(self, seed_value: int, max_length: int=10) -> str:
        """
        Generates a randomized string of named data from a list of common English words. 
        This is a helper method for building randomized trees.
        (The list of words is found in words.txt and can be found at 
        https://gist.github.com/deekayen/4148741.)

        Args:
            seed_value (int): a random number seed to ensure the generated trees are always
                              the same (for experimental purposes.)
            max_length (int, optional): the number of elements in the hierarchical name. 
                                        Defaults to 4.

        Returns:
            str: the named_data string.
        """
        # read the list of common English-language words into a list
        seed(seed_value)
        word_list = []
        with open('/spatialsync/client/words.txt') as file:
            for word in file:
                word_list.append(word.strip())

        number_elements = randint(2, max_length) # determine the number of elements in the named data string
        name = ""

        # generate the hierarchical name
        for i in range(number_elements):
            name = name + '/' + word_list[randint(0,len(word_list)-1)]

        # if the length of the string is even, add a version number between 1 and 10
        if number_elements % 2 == 0:
            version_number = '_v' + str(randint(1,10))
            name = name + '/' + version_number

        # create a divider to accommodate the geocode
        name = name + '/'

        return name

    def _generate_geocode(self, seed_value: int, geocode: str) -> str:
        """
        Generates a geocode for inserting named data in a tree.
        This is a helper method for building randomized trees. 

        Args:
            seed_value (int): a random number seed to ensure the generated trees are always
                              the same (for experimental purposes.)
            geocode (str): the Level 6 geocode that serves as the tree's root.

        Returns:
            str: the geocode which will be appended to the name.
        """
        seed_increment = seed_value
        insert_geocode = geocode
        valid_characters = '0123456789bcdefghjkmnpqrstuvwxyz'

        max_geocode_length = self.tree.max_depth
        # print(max_geocode_length)
        while len(insert_geocode) <= max_geocode_length:
            seed(seed_increment)
            insert_geocode = insert_geocode + valid_characters[randint(0, len(valid_characters) - 1)]
            seed_increment += 100

        # print(f'THE GENERATED GEOCODE: {insert_geocode}')
        return insert_geocode

    
    ######### MUTATORS #########
    def add_tree(self, new_tree: SpasyTree) -> None:
        """
        Adds a tree to the list of SpasyTrees the user is subscribed to.

        Args:
            new_tree (SpasyTree): the tree the user wants to subscribe to.
        """
        geocode = next(iter(new_tree.root.geocode)) # gets the first element of the geocode set, which is the root geocode
        self._trees[geocode] = new_tree
        self._subscribed_trees.append(geocode)

    @subscribed_trees.setter
    def subscribed_trees(self, new_subscription: str) -> None:
        self._subscribed_trees.add(new_subscription)

    def replace_tree(self, replacement_tree: SpasyTree) -> None:
        """
        Replace the current SpasyTree with a new version of a SpasyTree received from
        another Spasy group member.

        Args:
            replacement_tree (SpasyTree): the newer version of the SpasyTree.
        """
        self._tree = replacement_tree

    def update_tree(self, geocode: str, recent_changes: list) -> None:
        """
        Uses a priority queue that stores recent changes to another user's SpasyTree to 
        update the current user's SpasyTree. When done, the Merkle hash of the current
        user's SpasyTree root should match the hash of the other user's SpasyTree.

        Args:
            geocode (str): the geocode of the tree that requires an update.
            recent_changes (list): the priority queue that stores the recent changes.
        """
        # convert recent changes to a set in order to do set difference
        current_set = set(self.trees[geocode].recent_updates)
        update_set = set(recent_changes)

        # find differences
        set_difference = update_set.difference(current_set)
        # print(f'SET DIFF: {set_difference}')
        
        # handle differences if there are any
        if set_difference:
            for element in set_difference:
                timestamp = element[0]
                data = element[2]
                if element[1] == 'i':
                    self.add_data_to_tree(geocode, data, timestamp)
                elif element[1] == 'd':
                    self.remove_data_from_tree(geocode, data, timestamp)

        # check that the hashes match 

    def add_data_to_tree(self, geocode: str, data_to_add: str, timestamp: str="") -> None:
        """
        Inserts named data in the SpasyTree.

        Args:
            data_to_add (str): the named data to be inserted in the SpasyTree.
            timestamp (str, optional): the timestamp from when the data was added 
                                       to another tree. 
                                       Defaults to "", which occurs when the caller 
                                       is the data's publisher.
        """
        #print(f'DATA BEING ADDED: {data_to_add}')
        if timestamp == "":
            timestamp = str(time.time())
        #print(f'ADD DATA GEOCODE: {geocode}')
        self._trees[geocode].insert(data_to_add)
        self.trees[geocode].add_to_recent_updates((timestamp, 'i', data_to_add))

    def remove_data_from_tree(self, geocode: str, delete_data: str, timestamp: str="") -> None:
        """
        Deletes named data from the SpasyTree.

        Args:
            delete_data (str): the named data to delete.
            timestamp (str, optional): the timestamp from when the data was deleted 
                                       from another tree. 
                                       Defaults to "", which occurs when the caller is 
                                       the one publishing the deletion. 
        """
        data_to_delete = delete_data.lower()
        delete_geocode = delete_data.split('/')[-1]

        # if the data isn't in the tree, exit without doing anything; let the user know that nothing was deleted
        if not self.trees[geocode].find_data(data_to_delete):
            print(f"Sorry, but '{data_to_delete}' associated with the geocode '{delete_geocode}' is not in the tree.")
            return 

        else: 
            if timestamp == "":
                timestamp = time.time()
            print(f'DELETE: {timestamp, delete_data}')

            self._trees[geocode].delete(self._trees[geocode].root, delete_data, self._trees[geocode].root.length_geocode())
            self._trees[geocode].add_to_recent_updates((str(timestamp), 'd', delete_data))

    
    ######### OTHER #########
    def is_newer_tree(self, tree_geocode: str, sync_tree_hash: str) -> bool:
        """
        When a Sync Interest is received, the hashcodes must be compared.

        Args:
            tree_geocode (str): the current tree's geocode.
            sync_tree_hash (str): the root hashcode of a SpasyTree.

        Returns:
            bool: False if they match;
                  True otherwise.
        """
        if self._trees[tree_geocode].root.hashcode == sync_tree_hash:
            print(f'The tree is already up-to-date.')
            return False
        # # THIS DOES NOT APPLY TO THE CURRENT VERSION, AS OLD HASHES AREN'T KEPT
        # elif sync_tree_hash in self._tree._recent_changes:
        #     print(f'That is an older version of the tree.')
        #     return False
        else:
            print(f'This is a newer version of the tree. Send an Interest packet.')
            return True

    def search(self, data_to_find: str) -> bool:
        """
        Find all of the geohashes in which the named data is stored.

        Args:
            data_to_find (str): the named data being sought.

        Returns:
            list: a list of geohashes where the data is stored.
        """
        return self._tree.find_data(data_to_find)
    
    def search_without_geocode(self, data_to_find: str, geocode_list: list | None = None) -> list:
        """
        Checks for data in the tree independently of the geocode it is associated with. For example,
        if a user is looking for /some/data, that may exist as /some/data/dpwhwts0123 and 
        /some/data/dpwhwt0bcqr. This method will find both.

        Args:
            data_to_find (str): the named data (independent of geocode) being sought.
            geocode_list (list | None, optional): a list of geocodes where the named data can be found. 
                                                  Defaults to None.

        Returns:
            list: a list of geocodes where the named data can be found.
        """
        return self._tree.find_data_without_geocode(self._tree.root, data_to_find, geocode_list)
    
    def gather_all_data_by_namespace(self, geocode: str) -> dict:
        """
        Takes all of the data from the SpasyTree and organizes it by namespace.

        Returns:
            dict: a dictionary containing all of the data in the tree
                  organized into namespaces.  
        """
        return self._trees[geocode].find_data_by_namespace(self._trees[geocode].root)
    
    def gather_all_data_by_geocode(self, geocode: str) -> dict:
        """
        Takes all of the data from the SpasyTree and organizes it by geocode.

        Returns:
            dict: a dictionary containing all of the data in the tree
                  organized into geocodes. 
        """
        return self._trees[geocode].find_data_by_geocode(self._trees[geocode].root)
    
    def is_subscribed(self, named_data: str) -> bool:
        """_summary_

        Args:
            named_data (str): the hierarchical name contained in the Notification Interest

        Returns:
            bool: True, if the user subscribes to the tree;
                  False, otherwise.
        """
        # NOTE: a check would be required at a higher level to ensure this was a SPASY string to begin with
        # i.e., does the Notification Interest belong to SPASY? 
        # this is unnecessary for testing the algorithm
        geocode = named_data.split('/')[-1] # assumes the geocode is the final element
        root_geohash = geocode[0:6] # get the Level-6 geohash from the string
        if root_geohash in self._trees:
            return True
        else:
            print('That named item does not belong to any tree that is subscribed to.')
            return False
    
# testing
if __name__ == '__main__':
    print(f'\nTesting SPASY...\n')

    use_timestamps = True
    spasy = Spasy('dpwhwt')
    spasy2 = Spasy('dpwhwt')
    print(spasy.trees)
    name_to_add = 'alice/ball/_v0/dpwhwtmpz0'
    print(spasy.is_subscribed(name_to_add))
    spasy.add_data_to_tree('dpwhwt', name_to_add)
    print(spasy.trees['dpwhwt'].root)
    print(spasy.trees['dpwhwt'].root.hashcode)

    
    # spasy.build_tree_from_file('dpwhwt', 'spasy_tree.txt', 25000, use_timestamps)
    # start25 = time.time()
    # spasy.add_data_to_tree('dpwhwt', '/some/test/data/dpwhwtmpz0')
    # end25 = time.time()
    # print(f'Time 25,000: {end25 - start25}')

    # spasy2.build_tree_from_file('dpwhwt', 'spasy_tree.txt', 10000, use_timestamps)
    # start10 = time.time()
    # spasy2.add_data_to_tree('dpwhwt', '/some/test/data/dpwhwtmpz0')
    # end10 = time.time()
    # print(f'Time 10,000: {end10 - start10}') 
    # spasy.add_data_to_tree('dpwhwt', '/some/test/data/to/add/dpwhwt4bzh')
    # print(spasy.trees['dpwhwt'].root)
    # print(spasy.gather_all_data_by_namespace('dpwhwt'))
    # print(f'RECENT UPDATES: {spasy.trees['dpwhwt'].recent_updates}')
    # spasy.remove_data_from_tree('dpwhwt', '/some/test/data/dpwhwtbarq')
    # print(f'RECENT UPDATES AFTER DELETION: {spasy.trees['dpwhwt'].recent_updates}')
    # spasy.remove_data_from_tree('dpwhwt', '/some/test/data/to/add/dpwhwt4bzh')
    # spasy.remove_data_from_tree('dpwhwt', '/some/test/data/dpwhwtpqy1')
    # print(f'RECENT UPDATES WITH SUCCESSFUL DELETION: {spasy.trees['dpwhwt'].recent_updates}')
    # new_tree = SpasyTree(9, 30, Node('dvqrcq'))
    # print(new_tree.root)
    # spasy.add_tree(new_tree)
    # spasy.add_data_to_tree('dvqrcq', '/some/new/data/dvqrcqbcdg')
    # print(spasy.trees)
    # print(spasy.trees['dvqrcq'].root.data)
    # start = time.time()
    # spasy.build_tree_from_file('dpwhwt', "spasy_tree.txt", 3, use_timestamps)
    # update_value = spasy.trees['dpwhwt'].recent_updates
    # end = time.time()
    # print(f'TOTAL: {end - start}')
    # print(spasy.trees['dpwhwt'].root)
    # new_tree = SpasyTree(9, 30, Node('dpwhwt'))
    # spasy.add_tree(new_tree)
    # print(f'AGAIN: {spasy.trees['dpwhwt'].root}')
    # print(f'THE HASH: {spasy.trees['dvqrcq'].root.hashcode}')
    # print(f'THE OTHER: {spasy.trees['dpwhwt'].root.hashcode}')
    # print(f'TREES: {spasy.trees}')
    # print(spasy.is_newer_tree('dpwhwt', spasy.trees['dvqrcq'].root.hashcode))
    # spasy.update_tree('dpwhwt', update_value)
    # pprint(f'RECENT UPDATES: {spasy.trees['dpwhwt'].recent_updates}')
    # print(update_value)
    # print(spasy.is_newer_tree('dpwhwt', spasy.trees['dvqrcq'].root.hashcode))
    # spasy2 = Spasy('dpwhwt')
    # spasy2.build_tree_from_file('dpwhwt', "spasy_tree.txt", 10, use_timestamps)
    # #print(spasy.trees['dpwhwt'].root)
    # # print(spasy.gather_all_data_by_namespace('dpwhwt'))
    # # print(spasy.gather_all_data_by_geocode('dpwhwt'))
    # spasy.remove_data_from_tree('dpwhwt', "/there/world/product/plural/our/colony/sign/less/_v7/dpwhwt829w")
    # pprint(f'RECENT UPDATES: {spasy.trees['dpwhwt'].recent_updates}')
    
    # # # spasy._create_experiment_tree(100000, 10, use_timestamps)
    # spasy.build_tree_from_file('spasy_tree.txt', 100, use_timestamps)
    
    # spasy2 = Spasy('dpwhwt')
    # spasy2.build_tree_from_file('spasy_tree.txt', 100, use_timestamps)

    # hash_to_start = spasy.tree.root.hashcode == spasy2.tree.root.hashcode
    # start_build = time.time()
    # spasy.build_tree(10000) # build a tree with six elements
    # end_build = time.time()

    # print(f'Time to build tree: {end_build - start_build}')
    # # print(f'Time to insert 25 elements into the tree: {end_insert - start_insert}')

    
    # # spasy2 = Spasy('dpwhwt')
    # # spasy2.build_tree(10000)

    # spasy2 = Spasy('dpwhwt')
    # for element in spasy.recent_updates:
    #     data = element[2]
    #     timestamp = element[0]
    #     spasy2.add_data_to_tree(data, timestamp)

    # hash_to_start = spasy.tree.root.hashcode == spasy2.tree.root.hashcode

    # print(f'\n######### TESTING THE RECENT UPDATES #########\n')
    # print(f'\n######### NEWER TREE? #########\n')
    # spasy2.add_data_to_tree('/some/test/data/dpwhwtmpz0') # add something to the second tree
    # spasy2.add_data_to_tree('/second/piece/of/data/dpwhwtsh00')
    # spasy2.add_data_to_tree('/extra/data/dpwhwtsh00')
    # spasy2.add_data_to_tree('/some/data/dpwhwts021')
    # spasy2.add_data_to_tree('/extra/data/to/add/dpwhwtsp00')
    # spasy2.add_data_to_tree('/some/data/dpwhwtsz00')
    # spasy2.add_data_to_tree('/some/more/data/dpwhwtsb00')
    # spasy2.add_data_to_tree('/some/testing/data/dpwhwtsm00')
    # spasy2.add_data_to_tree('/some/data/dpwhwtsn00')
    # spasy2.add_data_to_tree('/second/piece/of/data/dpwhwts100')
    # spasy2.add_data_to_tree('/extra/data/dpwhwts200')
    # spasy2.add_data_to_tree('/extra/data/to/add/dpwhwtsh00')
    # spasy2.add_data_to_tree('/some/data/dpwhwtsh00')
    # spasy2.add_data_to_tree('/some/more/data/dpwhwtsh00')
    # spasy2.add_data_to_tree('/some/more/data//dpwhwtsmnz')
    # spasy2.add_data_to_tree('/some/testing/data/dpwhwtsh00')
    # spasy2.add_data_to_tree('/some/data/dpwhwtshpq')
    # spasy2.add_data_to_tree('/second/piece/of/data/dpwhwtsprt')
    # spasy2.add_data_to_tree('/extra/data/dpwhwts9bz')
    # spasy2.add_data_to_tree('/extra/data/to/add/dpwhwtspc1')
    # spasy2.add_data_to_tree('/some/data/dpwhwtspcd')
    # spasy2.add_data_to_tree('/some/more/data/_v1/dpwhwtsmnz')

    


    # before_the_update = spasy.tree.root.hashcode == spasy2.tree.root.hashcode

    # start = time.time()
    # spasy.update_tree(spasy2.tree.root.hashcode, spasy2.recent_updates) # update the first tree
    # end = time.time()
    
    # # print(f'\n######### THE FIRST TREE #########\n')
    # # print(spasy.tree.root)

    # # print(f'\n######### THE SECOND TREE #########\n')
    # # print(spasy2.tree.root)
    # print(f'\n######### DO THE TREES HAVE THE SAME HASH TO START? {hash_to_start}')
    # print(f'\n######### DO THE TREES HAVE THE SAME HASH BEFORE THE UPDATE TO SPASY? {before_the_update}')
    # print(f'\n######### DO THE TREES HAVE THE SAME HASH AFTER THE UPDATE? {spasy.tree.root.hashcode == spasy2.tree.root.hashcode}')
    # print(f'{spasy.tree.root.hashcode} and {spasy2.tree.root.hashcode}')
    # print(f'\n######### HOW LONG DID IT TAKE TO UPDATE THE TREE? {end - start}')

    # # TESTING REMAINING METHODS
    # print(f'\n######### TESTING OTHER METHODS #########')
    # print(spasy.search('/some/test/data'))
    # print(spasy.search('/some/test/data/dpwhwtmpz0v'))
    # print(spasy.search_without_geocode('/some/test/data'))
    # print(f'DATA BY GEOCODE:')
    # pprint(spasy.gather_all_data_by_geocode())
    # print(f'DATA BY NAMESPACE:')
    # pprint(spasy.gather_all_data_by_namespace())
    # spasy.remove_data_from_tree('/some/test/data/dpwhwtmpz0v')
    # print(f'DATA BY NAMESPACE AFTER REMOVAL:')
    # pprint(spasy.gather_all_data_by_namespace())
    # print(f'RECENT UPDATES:')
    # pprint(spasy2.recent_updates)
    # pprint(spasy.recent_updates)
    # print(f'SIZE: {asizeof.asizeof(spasy2.tree)}')

    

    


    # print(spasy.tree.root)
    # pprint(spasy.gather_all_data_by_namespace())
    # pprint(spasy.gather_all_data_by_geocode())
    # print(f'Time to build tree: {end - start}')
    # print(spasy.tree.recent_changes)
    # other_tree = SpasyTree(10, Node('dpwhwts'))

    # # compare trees
    # print(f"\n######### COMPARE TREES BEFORE ADDING NEW DATA #########\n")
    # start = time.time()
    # print(spasy.is_newer_tree(other_tree.root.hashcode))
    # end = time.time()
    # print(end - start)

    # # add data, then compare trees
    # print(f"\n######### COMPARE TREES AFTER ADDING NEW DATA #########\n")
    # other_tree.insert('/data/test/dpwhwtsh000')
    # print(spasy.is_newer_tree(other_tree.root.hashcode))

    # # Sync related things to be added
    # print(f'\n######### SEND A SYNC INTEREST #########\n')

    # # replace tree
    # print(f'\n######### THE TREE BEFORE REPLACING IT #########\n')
    # print(spasy.tree.root)
    # geohash_tree.insert('/second/piece/of/data/dpwhwtsh000')
    # geohash_tree.insert('/extra/data/dpwhwtsh000')
    # geohash_tree.insert('/some/data/dpwhwts0214')
    # geohash_tree.insert('/extra/data/to/add/dpwhwtsp000')
    # geohash_tree.insert('/some/data/dpwhwtsz001')
    # geohash_tree.insert('/some/more/data/dpwhwtsb009')
    # geohash_tree.insert('/some/testing/data/dpwhwtsm00h')
    # geohash_tree.insert('/some/data/dpwhwtsn00s')
    # geohash_tree.insert('/second/piece/of/data/dpwhwts1000')
    # geohash_tree.insert('/extra/data/dpwhwts2000')
    # geohash_tree.insert('/extra/data/to/add/dpwhwtsh000')
    # geohash_tree.insert('/some/data/dpwhwtsh001')
    # geohash_tree.insert('/some/more/data/dpwhwtsh009')
    # geohash_tree.insert('/some/testing/data/dpwhwtsh00h')
    # geohash_tree.insert('/some/data/dpwhwtshpqs')
    # geohash_tree.insert('/second/piece/of/data/dpwhwtsprtu')
    # geohash_tree.insert('/extra/data/dpwhwts9bzx')
    # geohash_tree.insert('/extra/data/to/add/dpwhwtspc18')
    # geohash_tree.insert('/some/data/dpwhwtspcdq')
    # geohash_tree.insert('/some/more/data/dpwhwtsmnz4')
    # geohash_tree.insert('/some/testing/data/dpwhwtsm00h')
    # geohash_tree.insert('/some/data/dpwhwtsp00s')
    # geohash_tree.insert('/second/piece/of/data/dpwhwtsq000')
    # geohash_tree.insert('/extra/data/dpwhwtsvw0z')
    # geohash_tree.insert('/some/data/dpwhwtsm0p1')
    # print(geohash_tree.root)

    # start = time.time()
    # spasy.is_newer_tree(geohash_tree.root.hashcode)
    # spasy.replace_tree(geohash_tree)
    # end = time.time()
    # print(f'end: {end}, start: {start}; calculation = {end - start}')
    # print(f'The tree contains {asizeof.asizeof(geohash_tree)} bytes.')
    # print(f'\n######### THE TREE AFTER REPLACING IT #########\n')

    # # ADD, DELETE, AND FIND DATA
    # spasy.add_data_to_tree('/add/data/dpwhwtsh401')
    # print(f'\n########## THE TREE WITH ADDED DATA #########\n')
    # #print(spasy.tree.root)
    # print(f"FIND WITHOUT GEOCODE '/add/data' (should be ['dpwhwtsh300', 'dpwhwtsh001', 'dpwhwtsh000', 'dpwhwtsp000',"
    #       f" 'dpwhwtsq000', 'dpwtsh401']): {spasy.search('/add/data')}")
    # spasy.add_data_to_tree('/data/test/dpwhwtsb900')
    # print(f'\n######### THE TREE BEFORE REMOVAL #########\n')
    # print(spasy.tree.root)
    # spasy.remove_data_from_tree('/data/test/dpwhwtsb900')
    # print(f'\n########## THE TREE WITH DATA REMOVED #########\n')
    # print(spasy.tree.root)
    # print(f"FIND '/add/data/dpwhwtsh401' (should be True): {spasy.search('/add/data/dpwhwtsh401')}")
    # print(f"FIND '/data/test' (should be []): {spasy.search_without_geocode('/data/test')}")
    # print(f"FIND WITHOUT GEOCODE '/add/data' (should be ['dpwhwtsh300', 'dpwhwtsh001', 'dpwhwtsh000', 'dpwhwtsp000',"
    #       f" 'dpwhwtsq000', 'dpwtsh401']): {spasy.search_without_geocode('/add/data')}")
    # start = time.time()
    # print(f"\n#########FIND ALL DATA #########\n: {spasy.gather_all_data_by_namespace()}")
    # end = time.time()
    # print(f'THE TIME TO CONVERT TO NAMESPACE DICTIONARY: {end - start}')
    # start = time.time()
    # print(f'\n######### ORGANIZE ALL DATA BY GEOCODE #########\n: {spasy.gather_all_data_by_geocode()}')
    # end = time.time()
    # print(f'THE TIME TO CONVERT TO GEOCODE DICTIONARY: {end - start}')

    # TESTING recent_updates
    # updates_to_test = [(1727803768.6485171, 'insert', '/extra/data/to/add/dpwhwtsh900'), (1727803768.648532, 'insert', '/some/data/dpwhwtsh001'), \
    #                    (1727803768.648543, 'insert', '/some/more/data/dpwhwtsh009')]
    # heapify(updates_to_test)
    # print(f'\n######### UPDATE HEAP #########\n')
    # pprint(updates_to_test)
    # # testing tree merging
    # spasy1 = Spasy('dpwhwt')
    # count = 0
    # for element in updates_to_test:
    #     timestamp = element[0]
    #     data = element[2]
    #     count += 1
    #     spasy1.add_data_to_tree(data, timestamp)
    #     print(f'Count: {count}, and recent updates: {spasy1.recent_updates}')

    # print(f'COUNT AFTER ADDING TO SPASY 1: {count}')
    # print(f'SPASY 1 RECENT UPDATES')
    # pprint(spasy1.recent_updates)
    
    # spasy2 = Spasy('dpwhwt')
    # count = 0
    # for element in updates_to_test:
    #     timestamp = element[0]
    #     data = element[2]
    #     count += 1
    #     spasy2.add_data_to_tree(data, timestamp)

    # print(f'COUNT AFTER ADDING TO SPASY 2: {count}')
    # print(f'SPASY 2 RECENT UPDATES:')
    # pprint(spasy2.recent_updates)


    # print(f'\n######### TREE BEFORE UPDATE #########\n')
    # print(spasy1.tree.root)
    #spasy1.update_tree(spasy2.tree.root, spasy2.tree.recent_changes)
    # print(f'\n######### TREE AFTER UPDATE #########\n')
    # print(spasy1.tree.root)
    # print(f'\n######### TREE AFTER DELETE ##########\n')
    # spasy1.remove_data_from_tree('/extra/data/to/add/dpwhwtsh900')
    # spasy2.update_tree(spasy1.tree.root, spasy1.recent_updates)
    # spasy2.add_data_to_tree('/new/data/a1/dpwhwtqrp0h')
    #spasy2.update_tree(spasy1.tree.root, spasy1.tree.recent_changes)
    # print(spasy2.tree.root)
    # print(f'\n######### FIRST TREE CHANGES #########\n')
    # pprint(spasy1.tree.recent_changes)
    # print(f'\n######### SECOND TREE CHANGES #########\n')
    # pprint(spasy2.tree.recent_changes)
    # print(f'\n######### RECENT UPDATES #########\n')
    # print(f'SPASY 1: ')
    # pprint(spasy1.recent_updates)
    # print(f'SPASY 2')
    # pprint(spasy2.recent_updates)
