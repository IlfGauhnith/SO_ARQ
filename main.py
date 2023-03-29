from input_handler import InputHandler

BLOCK_SIZE = 512
DISK_SIZE = 8192
TOTAL_BLOCKS = DISK_SIZE//BLOCK_SIZE


class FATCluster:

    def __init__(self):
        self.is_free = True
        self.next_cluster = None
        self.internal_frag = 0

        self.file_name = ""  # Atributo com fim didático para printar a FAT de forma mais legível.


class Directory:

    def __init__(self, name):
        self.content = {}
        self.name = name


class File:

    def __init__(self, start_cluster, name, size):
        self.start_cluster = start_cluster
        self.name = name
        self.size = size


class FAT:

    def __init__(self):
        self.root = Directory("/")
        self.clusters = [FATCluster() for _ in range(0, TOTAL_BLOCKS)]
        self.free_storage = DISK_SIZE
        self.external_frag = 0

    def print_fat(self):
        res = ""
        for cluster in self.clusters:
            res = res + str(cluster) + " " + ("Livre" if cluster.is_free else "Ocupado") + " " + cluster.file_name + " " + ("frag:" + str(cluster.internal_frag) if cluster.internal_frag > 0 else "") + "\n"

        print(res)

    def get_next_free_block(self):
        for block in self.clusters:

            if block.is_free:
                self.free_storage = self.free_storage - BLOCK_SIZE
                block.is_free = False

                return block

    def add_block_to_free(self, block: FATCluster):
        block.is_free = True
        block.next_cluster = None
        block.internal_frag = 0

        self.free_storage = self.free_storage + BLOCK_SIZE
        self.clusters.append(block)

    def navegate_to_dir(self, path):
        try:
            dir = self.root
            path_splited = path[1:].split("/")

            if path_splited[0] != '':
                for sub_path in path_splited:
                    dir = dir.content[sub_path]

            return dir
        except KeyError:
            raise ValueError("Diretório não existe")

    @staticmethod
    def print_block_sequence(file: File):
        block = file.start_cluster
        res = ""
        while block:
            res = res + str(block) + " -> "
            block = block.next_cluster

        res = res[:-3]
        print(res)

    def print_dir(self, path):
        dir = self.navegate_to_dir(path)

        res = " ".join(dir.content.keys())
        print(res)

    def create_file(self, path, name: str, size: int):

        if self.free_storage < size:
            raise ValueError("Não armazenamento disponível suficiente no disco para armazenar esse arquivo")

        dir = self.navegate_to_dir(path)
        block = self.get_next_free_block()
        block.file_name = name

        file = File(block, name, size)
        if size < BLOCK_SIZE:
            block.internal_frag = BLOCK_SIZE - size

        data_counter = size - BLOCK_SIZE

        previous_block = file.start_cluster
        while data_counter > 0:
            block = self.get_next_free_block()
            block.file_name = name

            if data_counter < BLOCK_SIZE:
                block.internal_frag = BLOCK_SIZE - data_counter

            previous_block.next_cluster = block
            data_counter = data_counter - BLOCK_SIZE

            previous_block = previous_block.next_cluster
        dir.content[name] = file

        print("Arquivo " + file.name + " alocado com sucesso!")
        FAT.print_block_sequence(file)

    def create_dir(self, path, name):
        try:
            dir = self.navegate_to_dir(path)
            dir.content[name] = Directory(name)
        except KeyError:
            raise ValueError("Diretório já existe.")

        print("Diretório criado com sucesso!")

    def delete_file(self, path):
        filename = path.split("/")[-1]
        path = "/".join(path.split("/")[:-1])

        if path == '':
            path = '/'

        dir = self.navegate_to_dir(path)

        if filename not in dir.content.keys():
            raise ValueError("Arquivo não existe!")

        file = dir.content.pop(filename)

        cluster = file.start_cluster

        while cluster:
            cluster.is_free = True
            cluster.file_name = ""
            cluster.internal_frag = 0

            tmp_cluster = cluster.next_cluster
            cluster.next_cluster = None
            cluster = tmp_cluster
        print("Arquivo " + filename + " deletado com sucesso!")

    def delete_dir(self, path):
        dir = self.navegate_to_dir(path)

        if len(dir.content.keys()) > 0:

            for key, content in dir.content.copy().items():

                if isinstance(content, Directory):
                    self.delete_dir(path + "/" + content.name)

                elif isinstance(content, File):
                    self.delete_file(path + "/" + content.name)

        path_to_previous = "/".join(path.split("/")[:-1])
        if path_to_previous == '':
            path_to_previous = '/'

        self.navegate_to_dir(path_to_previous).content.pop(dir.name)
        print("Diretório " + path + " deletado com sucesso!")

def print_commands():
    print("COMANDOS")
    print("{0: <75}".format("ls <absolute_path>") + "Para listar o conteúdo de <absolute_path>")
    print("{0: <75}".format("mkdir <absolute_path> <dir_name>") + "Para criar um diretório vazio chamado <dir_name> em <absolute_path>")
    print("{0: <75}".format("touch <absolute_path> <file_name> <file_size_in_bytes>") + "Para criar um arquivo chamado <file_name> em <absolute_path> de tamanho <file_size_in_bytes>")
    print("{0: <75}".format("rmdir <absolute_path>") + "Para deletar o diretório em <absolute_path>")
    print("{0: <75}".format("destroy <absolute_path>") + "Para deletar o arquivo em <absolute_path>")
    print("{0: <75}".format("showFat") + "Para mostrar a tabela FAT")
    print("{0: <75}".format("help") + "Para mostrar os comandos")
    print("{0: <75}".format("exit") + "Para fechar o sistema de arquivos do WINTERMUTE XXIII")


if __name__ == "__main__":
    print("SISTEMA DE ARQUIVOS - WINTERMUTE XXIII \n")
    print_commands()

    fat = FAT()
    user_input = InputHandler.str_input(">")
    while True:

        try:
            command = user_input.split(" ")[0]
            arguments = user_input.split(" ")[1:]

            if command == "ls":
                fat.print_dir(arguments[0])

            elif command == "mkdir":
                fat.create_dir(arguments[0], arguments[1])

            elif command == "touch":
                fat.create_file(arguments[0], arguments[1], int(arguments[2]))

            elif command == "rmdir":
                fat.delete_dir(arguments[0])

            elif command == "destroy":
                fat.delete_file(arguments[0])

            elif command == "showFat":
                fat.print_fat()

            elif command == "help":
                print_commands()

            elif command == "exit":
                break

            else:
                print(user_input + " é um comando inválido.")

        except Exception as ex:
            print("ERROR")
            print(ex)

        user_input = InputHandler.str_input(">")
