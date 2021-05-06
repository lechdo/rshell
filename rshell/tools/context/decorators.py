from rshell.tools.params.project import default_params as __params

if __params.test_mode:
    print("ATTENTION - PROJET EN MODE TEST !!!")


def under_context(func):
    """
    Renvoie selon le contexte :

        - exécution : la fonction sans changement
        - test : un vstring bouchon composé du nom de la fonction
    :param func:
    :return:
    """

    def inner():
        return "{}-plug".format(func.__name__)

    if __params.test_mode:
        print("Test mode for {}.{}".format(func.__module__, func.__name__))
        return inner
    else:
        return func
