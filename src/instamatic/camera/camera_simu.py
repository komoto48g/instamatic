import atexit
import logging
import time

import numpy as np

from instamatic import config

logger = logging.getLogger(__name__)


class CameraSimu:
    """Simple class that simulates the camera interface and mocks the method
    calls."""

    def __init__(self, name='simulate'):
        """Initialize camera module."""
        super().__init__()

        self.name = name

        self.establish_connection()

        self.load_defaults()

        msg = f'Camera {self.get_name()} initialized'
        logger.info(msg)

        atexit.register(self.release_connection)

        # EMMENU variables
        self._image_index = 0
        self._exposure = self.default_exposure
        self._autoincrement = True
        self._start_record_time = -1

    def load_defaults(self):
        if self.name != config.settings.camera:
            config.load_camera_config(camera_name=self.name)

        self.streamable = True

        self.__dict__.update(config.camera.mapping)

    def get_image(self, exposure=None, binsize=None, **kwargs) -> np.ndarray:
        """Image acquisition routine. If the exposure and binsize are not
        given, the default values are read from the config file.

        Parameters
        ----------
        exposure : float
            Exposure time in seconds.
        binsize : int
            Which binning to use.

        Returns
        -------
        arr : np.ndarray
        """
        if exposure is None:
            exposure = self.default_exposure
        if not binsize:
            binsize = self.default_binsize

        dim_x, dim_y = self.get_camera_dimensions()

        dim_x = int(dim_x / binsize)
        dim_y = int(dim_y / binsize)

        time.sleep(exposure)

        arr = np.random.randint(256, size=(dim_x, dim_y))

        return arr

    def getMovie(self, n_frames, *, exposure: float = None, binsize: int = None, **kwargs):
        """"Movie acquisition routine. If the exposure and binsize are not
        given, the default values are read from the config file.

        Parameters
        ----------
        n_frames : int
            Number of frames to collect
        exposure : float
            Exposure time in seconds.
        binsize : int
            Which binning to use.

        Returns
        -------
        stack : List[np.ndarray]
        """
        return [self.get_image(exposure=exposure, binsize=binsize) for _ in range(n_frames)]

    def acquire_image(self) -> int:
        """For TVIPS compatibility."""
        return 1

    def is_camera_info_available(self) -> bool:
        """Check if the camera is available."""
        return True

    def get_image_dimensions(self) -> (int, int):
        """Get the binned dimensions reported by the camera."""
        binning = self.get_binning()
        dim_x, dim_y = self.get_camera_dimensions()

        dim_x = int(dim_x / binning)
        dim_y = int(dim_y / binning)

        return dim_x, dim_y

    def get_camera_dimensions(self) -> (int, int):
        """Get the dimensions reported by the camera."""
        return self.dimensions

    def get_name(self) -> str:
        """Get the name reported by the camera."""
        return self.name

    def establish_connection(self) -> None:
        """Establish connection to the camera."""
        res = 1
        if res != 1:
            raise RuntimeError(f'Could not establish camera connection to {self.name}')

    def release_connection(self) -> None:
        """Release the connection to the camera."""
        name = self.get_name()
        msg = f"Connection to camera '{name}' released"
        logger.info(msg)

    # Mimic EMMENU API

    def get_emmenu_version(self) -> str:
        return 'simu'

    def get_camera_type(self) -> str:
        return 'SimuType'

    def get_current_config_name(self) -> str:
        return 'SimuCfg'

    def set_autoincrement(self, value):
        self._autoincrement = value

    def get_autoincrement(self):
        return self._autoincrement

    def set_image_index(self, value):
        self._image_index = value

    def get_image_index(self):
        return self._image_index

    def stop_record(self) -> None:
        t1 = self._start_record_time
        if t1 >= 0:
            t2 = time.perf_counter()
            n_images = int((t2 - t1) / self._exposure)
            new_index = self.get_image_index() + n_images
            self.set_image_index(new_index)
            print('stop_record', t1, t2, self._exposure, new_index)
            self._start_record_time = -1
        else:
            pass

    def start_record(self) -> None:
        self._start_record_time = time.perf_counter()

    def stop_liveview(self) -> None:
        self.stop_record()
        print('Liveview stopped')

    def start_liveview(self, delay=3.0) -> None:
        time.sleep(delay)
        print('Liveview started')

    def set_exposure(self, exposure_time: int) -> None:
        self._exposure = exposure_time / 1000

    def get_exposure(self) -> int:
        return self._exposure

    def get_timestamps(self, start_index, end_index):
        return list(range(20))

    def get_binning(self):
        return self.default_binsize

    def write_tiffs(self, start_index: int, stop_index: int, path: str, clear_buffer=True) -> None:
        pass
