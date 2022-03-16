# pyright: reportUnknownVariableType=false
from ..utils.directory import script_dir, cwd
from .parse.detector import Detector, Parsable, time
from .configuration import Configuration

class Test(Detector):

    def onParsed(self, parsed: Parsable):
        print("YEP")

@cwd(script_dir(__file__), '..', '..', 'configurations')
def test_load():
    detector = Test('test_1.yaml', Configuration())
    detector.start()
    time.sleep(40)
    detector.kill()
