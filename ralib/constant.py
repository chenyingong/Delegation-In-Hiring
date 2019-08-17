class Const:
    class ConstError(TypeError):
        pass

    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, key, value):
        print()
        if key in self.__dict__.keys():
            raise self.ConstError("Can't change a const variable: {}".format(key))

        if not key.isupper():
            raise self.ConstCaseError("Const variable must be combined with upper"
                                      "letters: {}".format(key))

        self.__dict__[key] = value
