import argparse

class Query:
    def __init__(self, args):
        
        self.filters = args.filters
        self.text = args.text
        self.fields = args.fields
        self.sort = args.sort
        self.group_packs = args.group_packs

class Arguments:
    def __init__(self):
        
        self.text = None
        self.filters = None
        self.fields = None
        self.sort = None
        self.group_packs = None
        
        self.__args = argparse.ArgumentParser()
        self.__args.add_argument(
            "--text_query", 
            default = "", 
            type = str
        )
        self.__args.add_argument(
            "--fields", 
            nargs = '+', 
            default = ["id", "name", "avg_rating", "tags", "type"], 
            type = str
        )
        self.__args.add_argument(
            "--tags", 
            nargs = '+', 
            type = str
        )
        self.__args.add_argument(
            "--filetypes", 
            nargs = '+',
            default = "wav",
            type = str
        )
        self.__args.add_argument(
            "--duration_range", 
            nargs = 2, 
            type = float
        )
        self.__args.add_argument(
            "--rating_range", 
            nargs = 2, 
            type = float
        )
        self.__args.add_argument(
            "--sort", 
            nargs = 1, 
            choices = ["rating_desc", "rating_asc", "downloads_desc", "downloads_asc", "duration_desc", "duration_asc"], 
            default = "rating_desc", 
            type = str
        )
        self.__args.add_argument(
            "--group_packs", 
            nargs = 1, 
            choices = [0, 1], 
            default = 0, 
            type = int
        )
        self.build()
        
    def build(self):
        
        args = self.__args.parse_args()
        
        if args.filetypes and len(args.filetypes) > 1:
            filters = "type:(" + " OR ".join(args.filetypes) + ") "
        elif args.filetypes:
            filters = "type:{} ".format(args.filetypes[0])
        else:
            filters = ""
        
        filters += "tag:(" + " OR ".join(args.tags) + ") " if args.tags else ""
        
        filters += " avg_rating:[{a} TO {b}]".format(
            a=min(args.rating_range), 
            b=max(args.rating_range)
        ) if args.rating_range else ""
        
        filters += " duration:[{a} TO {b}]".format(
            a=min(args.duration_range), 
            b=max(args.duration_range)
        ) if args.duration_range else ""
        
        self.text = args.text_query if args.text_query else None
        self.filters = filters if filters != "" else None
        self.fields = ",".join(args.fields)
        self.sort = args.sort
        self.group_packs = args.group_packs
        
        return self



