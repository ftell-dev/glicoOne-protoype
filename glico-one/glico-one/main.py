from kivy.app import App
from kivy.config import Config
from kivy.uix.screenmanager import ScreenManager, Screen

from config.settings import APP_NAME, SCREEN_WIDTH, SCREEN_HEIGHT
from database.local_storage import LocalStorage
from hardware.printer import ReceiptPrinter
from hardware.sensor import GlucoseSensor
from services.authentication import AuthenticationService
from services.measurement_service import MeasurementService
from services.printer_service import PrinterService

from config.ui.screens.loading import LoadingScreen
from config.ui.screens.menu import MenuScreen
from config.ui.screens.measurement import MeasurementScreen
from config.ui.screens.result import ResultScreen
from config.ui.screens.id_login import IDLoginScreen
from config.ui.screens.qr_login import QRLoginScreen


Config.set("graphics", "width", SCREEN_WIDTH)
Config.set("graphics", "height", SCREEN_HEIGHT)
Config.set("graphics", "resizable", "0")


class GlicoOneApp(App):

    def build(self):
        self.title = APP_NAME
        self.storage = LocalStorage()
        self.sensor = GlucoseSensor()
        self.authentication = AuthenticationService(self.storage)
        self.measurements = MeasurementService(self.sensor, self.storage)
        self.printer = PrinterService(ReceiptPrinter())
        self.current_user = None

        self.manager = ScreenManager()

        loading = Screen(name="loading")
        loading.add_widget(
            LoadingScreen(self)
        )

        self.manager.add_widget(loading)

        self.show_loading()

        return self.manager

    def show_loading(self):
        self.manager.current = "loading"

    def show_menu(self):

        if "menu" not in self.manager.screen_names:

            menu = Screen(name="menu")
            menu.add_widget(MenuScreen(self))

            self.manager.add_widget(menu)

        self.manager.current = "menu"

    def show_id_login(self):
        self._show_screen("id_login", IDLoginScreen)

    def show_qr_login(self):
        self._show_screen("qr_login", QRLoginScreen)

    def _show_screen(self, name, widget_class):
        if name not in self.manager.screen_names:
            screen = Screen(name=name)
            screen.add_widget(widget_class(self))
            self.manager.add_widget(screen)
        self.manager.current = name

    def login(self, identifier, password, require_cpf=True):
        self.current_user = self.authentication.login(identifier, password, require_cpf=require_cpf)
        self.start_measurement(logged_in=True)

    def start_measurement(self, logged_in=False):

        if "measurement" in self.manager.screen_names:
            self.manager.remove_widget(
                self.manager.get_screen("measurement")
            )

        measurement = Screen(name="measurement")

        measurement.add_widget(
            MeasurementScreen(
                self,
                logged_in=logged_in,
            )
        )

        self.manager.add_widget(measurement)

        self.manager.current = "measurement"

    def show_result(self, measurement, logged_in=False):

        if "result" in self.manager.screen_names:
            self.manager.remove_widget(
                self.manager.get_screen("result")
            )

        result = Screen(name="result")

        result.add_widget(
            ResultScreen(
                self,
                measurement=measurement,
                logged_in=logged_in
            )
        )

        self.manager.add_widget(result)

        self.manager.current = "result"


if __name__ == "__main__":
    GlicoOneApp().run()