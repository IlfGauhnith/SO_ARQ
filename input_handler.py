class InputHandler:
    @staticmethod
    def int_input(msg, interval=(0, 0)):
        while True:
            try:
                user_input = int(input(msg))

                if interval[0] < interval[1]:
                    if not (interval[0] <= user_input <= interval[1]):
                        raise ValueError()

                break
            except ValueError:
                print("Entrada inválida.\n")

        return user_input

    @staticmethod
    def str_input(msg):
        while True:
            try:
                user_input = str(input(msg))

                if len(user_input) == 0:
                    raise ValueError()

                break
            except ValueError:
                print("Entrada inválida.\n")

        return user_input

    @staticmethod
    def bool_input(msg):
        while True:
            try:
                user_input = input(msg).upper()

                if user_input not in ('SIM', 'NAO', 'S', 'N'):
                    raise ValueError()

                break
            except ValueError:
                print("Entrada inválida.\n")

        if user_input == 'SIM' or user_input == 'S':
            return True
        else:
            return False
