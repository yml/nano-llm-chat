from chat import app


def pytest_configure():
    """
    Load nanodjango project and make sure the ninja routes are mounted.
    """
    app._prepare(is_prod=False)

