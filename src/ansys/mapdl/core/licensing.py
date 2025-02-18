# Copyright (C) 2016 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module for licensing and license serve checks."""

import os
import socket

# Subprocess is needed to start the backend. But
# the input is controlled by the library. Excluding bandit check.
import subprocess  # nosec B404
import time

from ansys.mapdl.core import _HAS_ATP, LOG
from ansys.mapdl.core.errors import LicenseServerConnectionError
from ansys.mapdl.core.misc import threaded_daemon

if _HAS_ATP:
    from ansys.tools.path import get_mapdl_path, version_from_path

LIC_PATH_ENVAR = "ANSYSLIC_DIR"
LIC_FILE_ENVAR = "ANSYSLMD_LICENSE_FILE"
APP_NAME = "FEAT_ANSYS"  # TODO: We need to make sure this is the type of feature we need to checkout.
LIC_TO_CHECK = ["mech_1"]

LICENSES = {
    "ansys": "Ansys Mechanical Enterprise",
    "meba": "Ansys Mechanical Enterprise Solver",
    "mech_2": "Ansys Mechanical Premium",
    "mech_1": "Ansys Mechanical Pro",
    "preppost": "Mechanical Enterprise PrepPost",
}
ALLOWABLE_LICENSES = list(LICENSES)

## Regarding license checking.
# The available licenses we can check against are (in order of
# complete/comprehensiveness):
# 1. ``Ansys`` Enterprise license (the most complete)
# 2. ``meba`` Mechanical Enterprise license
# 3. ``mech_2`` Premium license
# 4. ``mech_1`` Pro license` (the most limited)
# To keep very general, and since we need just to be able to solve, we are going to check against the lower license (``mech_1``).

# TODO: Implement a warning for insufficient license rights.


class LicenseChecker:
    """License checker class.

    Two methods are used and exposed with the :func:`LicenseChecker.start` method:

    * Check the ``licdebug`` log file for errors.
    * Check the available mechanical licenses using ``ansysli_util`` executable.

    Parameters
    ----------
    timeout : float, optional
        Timeout for the licensing log file check.

    """

    def __init__(self, timeout=30, verbose=None):
        self._license_file_msg = []
        self._license_file_success = None

        self._license_checkout_msg = []
        self._license_checkout_success = None
        self._timeout = timeout

        if verbose is not None:
            raise DeprecationWarning(
                "The argument 'verbose' has been deprecated, please use loggers from the logging module."
            )

        self._lic_file_thread = None
        self._checkout_thread = None

        self._stop = False
        self._is_connected = False

    @property
    def stop(self):
        return self._stop

    @stop.setter
    def stop(self, value):
        if bool(value):
            LOG.debug("Attempting to stop the license checker.")
        self._stop = bool(value)

    @property
    def is_connected(self):
        return self._is_connected

    @is_connected.setter
    def is_connected(self, value):
        if bool(value):
            LOG.debug("PyMAPDL has connected to a MAPDL session.")
        self._is_connected = bool(value)

    @threaded_daemon
    def check_license_file(self):
        try:
            self._check_license_file(self._timeout)
        except Exception as error:
            self._license_file_success = False
            self._license_file_msg.append(str(error))
        else:
            self._license_file_success = True

    @threaded_daemon
    def checkout_license(self, host=None):
        try:
            self._check_mech_license_available(host)
        except Exception as error:
            self._license_checkout_success = False
            self._license_checkout_msg.append(str(error))
        else:
            self._license_checkout_success = True

    def start(self, license_file=True, checkout_license=False):
        """Start monitoring the license file and attempt a license checkout.

        Parameters
        ----------
        license_file : bool, optional
            Start the license file thread.
        checkout_license : bool, optional
            Start the checkout license thread.  By default this is
            disabled.

        """
        if license_file and _HAS_ATP:
            self._lic_file_thread = self.check_license_file()
        if checkout_license:
            self._checkout_thread = self.checkout_license()

    def wait(self):
        """Wait until the license checks are complete or have timed out."""
        if self._lic_file_thread is not None:
            self._lic_file_thread.join()
        if self._checkout_thread is not None:
            self._checkout_thread.join()

    def check(self):
        """Report if the license checkout or license check was successful.

        It first checks the output from the license file and later the
        output from the checkout process.

        Returns
        -------
        bool
            ``True`` When license successfully checked out, ``False``
            when license check failed and nothing to report.  Checkout
            failure will raise
            :class:`ansys.mapdl.core.errors.LicenseServerConnectionError``.

        Raises
        ------
        LicenseServerConnectionError
            If there were any errors during the license checkout or
            license file check.

        """
        if self._license_file_success:
            return True
        elif self._license_file_success is False:
            raise LicenseServerConnectionError("\n".join(self._license_file_msg))

        if self._license_checkout_success:
            return True
        elif self._license_checkout_success is False:
            raise LicenseServerConnectionError("\n".join(self._license_checkout_msg))

        return False  # pragma: no cover

    def _check_license_file(self, timeout=30, notify_at_second=5):  # pragma: no cover
        """Check the output of the license client log for connection error.

        Expect type of errors with 'DENIED' in the header such as:
        ```
        2021/09/06 22:39:38    DENIED              ansys                           21.2 (2021.0512)             1/0/0/0                 1/1/1/1   10268:FEAT_ANSYS:gayuso@AAPDDqVK5WqNLrt.win.ansys.com:winx64   7368:192.168.18.10
                    Request name ansys does not exist in the licensing pool.
                    Cannot connect to license server system.
                    The license server manager (lmgrd) has not been started yet,
                    the wrong port@host or license file is being used, or the
                    port or hostname in the license file has been changed.
                    Feature:       ansys
                    Server name:   192.168.18.10
                    License path:  1055@AAPDDqVK5WqNLrt;
                    FlexNet Licensing error:-15,578.  System Error: 10049 "WinSock: Invalid address"
        ```
        On the other side, successful license checkout will print `CHECKOUT       $APPNAME` in the file, such as:
        ```
        2021/09/20 12:59:49    CHECKOUT            FEAT_ANSYS                      21.2 (2021.0512)             1/1/1/1                 1/1/1/1   11704:FEAT_ANSYS:gayuso@AAPDDqVK5WqNLve.win.ansys.com:winx64   6884:192.168.56.1
        ```
        for `FEAT_ANSYS`.

        Parameters
        ----------
        timeout : int, optional
            Time to keep checking the license log file for errors. Default to 10 (seconds).

        Raises
        ------
        LicenseServerConnectionError
            If there is an error message in the license log file.
        TimeoutError
            Exceeded ``timeout`` while waiting for the license log file.

        """
        licdebug_file = os.path.join(
            get_ansys_license_debug_file_path(),
            get_ansys_license_debug_file_name(),
        )
        file_iterator = get_ansys_license_debug_file_tail(licdebug_file)

        if self._check_license_file_iterator(
            file_iterator, licdebug_file, timeout, notify_at_second
        ):
            return True

    def _check_license_file_iterator(
        self, file_iterator, licdebug_file, timeout=30, notify_at_second=5
    ):
        """Loop over iterator"""
        max_time = time.time() + timeout
        notification_time = time.time() + notify_at_second
        notification_bool = True
        while time.time() < max_time:
            if self.stop:  # pragma: no cover
                LOG.debug("The license checker has received a stop signal.")
                raise Exception("The license checker has been stopped.")

            if self.is_connected:  # pragma: no cover
                LOG.debug("The MAPDL session got connected. Stopping license check.")
                return True

            if (
                time.time() > notification_time and notification_bool
            ):  # pragma: no cover
                msg = (
                    "PyMAPDL is taking longer than expected to connect to an MAPDL session.\n"
                    "Checking if there are any available licenses..."
                )
                LOG.debug(msg)
                print(msg)
                notification_bool = False

            msg = next(file_iterator)
            if msg:
                LOG.debug(f"Output from {licdebug_file}:\n{msg}")

            if "DENIED" in msg:
                # read to the end of the file
                time.sleep(0.05)  # permit flush
                messages = [msg]
                while True:
                    msg = next(file_iterator).strip()
                    if not msg:
                        break
                    messages.append(msg)  # pragma: no cover

                raise LicenseServerConnectionError("\n".join(messages))

            if "CHECKOUT" in msg:
                # successful license checkout
                return True

        raise TimeoutError(
            f"Exceeded timeout of {timeout} seconds while examining:\n{licdebug_file}"
        )

    def _checkout_license(self, lic, host=None, port=2325):
        """Check if a license is available using the Ansys license utility.

        It uses it own process.

        Parameters
        ----------
        lic : str
            License type.  For example, ``"meba".  one of the following:

            1. ``"Ansys"`` Enterprise license (the most complete)
            2. ``"meba"`` Mechanical Enterprise license
            3. ``"mech_2"`` Premium license
            4. ``"mech_1"`` Pro license` (the most limited)
        host : str, optional
            Host to attempt to checkout license from.  When set, this
            overrides any settings from the default license path.
        port : int, optional
            Port on the host to connect to.  Only used when ``host`` is set.

        """
        if lic.lower() not in ALLOWABLE_LICENSES:  # pragma: no cover
            raise ValueError(f"Invalid license '{lic}'")

        ansysli_util_path = get_ansys_license_utility_path()

        if not os.path.isfile(ansysli_util_path):  # pragma: no cover
            raise FileNotFoundError(
                "Ansys licensing path exists but ansysli_util not found at:\n"
                f"{ansysli_util_path}"
            )

        # allow the specification of ip and port
        env = os.environ.copy()
        if host is not None and port is not None:  # pragma: no cover
            env["ANSYSLI_SERVERS"] = f"{host}:{port}"
            env["ANS_FLEXLM_DISABLE_DEFLICPATH"] = "TRUE"

        tstart = time.time()
        # ansysli_util_path is controlled by the library.
        # Excluding bandit check.
        process = subprocess.Popen(
            [f'"{ansysli_util_path}"', "-checkout", f"{lic}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
        )  # nosec B603
        output = process.stdout.read().decode()

        t_elap = time.time() - tstart
        LOG.debug(f"License check complete in {t_elap:.2} seconds.\n")
        LOG.debug(output)

        return output

    def _check_mech_license_available(
        self, host=None, licenses=None
    ):  # pragma: no cover
        """Check if there mechanical license available by running 'ansysli_util'.

        This uses the default configuration available to MAPDL.

        .. warning::
          This method to check the license server status is not stable.  It
          is very likely it will show license not available when it actually
          is.

        Parameters
        ----------
        host : str, optional
            Override the default license server.  By default, use the
            values available in the Ansys license file.
        license : str, list, optional
            A list or single license to check for.  One or more of the
            following:

            1. ``"Ansys"`` Enterprise license (the most complete)
            2. ``"meba"`` Mechanical Enterprise license
            3. ``"mech_2"`` Premium license
            4. ``"mech_1"`` Pro license` (the most limited)

        Returns
        -------
        bool
            Returns True when the license exists.

        Raises
        ------
        LicenseServerConnectionError
            When errors messages found in the output of the license file.

        """

        if licenses is None:
            licenses = LIC_TO_CHECK
        elif isinstance(licenses, str):
            licenses = [licenses]

        msg1 = "No such feature exists"
        msg2 = "The server is down or is not responsive."
        for each_license in licenses:
            output = self._checkout_license(each_license, host)
            if msg1 in output or msg2 in output:
                raise LicenseServerConnectionError(output)

        return True


def get_ansys_license_debug_file_tail(licdebug_file, start_timeout=10, debug=False):
    """Get each of the licdebug file messages.

    This method keeps the ``licdebug`` file open checking for complete messages.
    It yields one message at a time when called.

    Parameters
    ----------
    licdebug_file : str
        Path to the ``licdebug`` file.wh
    start_timeout : float, optional
        Maximum timeout to wait until the file exists.

    Yields
    ------
    msg : str
        Message formatted as a single string.

    """
    # wait until file exists
    max_time = time.time() + start_timeout
    while not os.path.isfile(licdebug_file):  # pragma: no cover
        time.sleep(0.01)
        if time.time() > max_time:
            raise TimeoutError(
                f"Exceeded {start_timeout} seconds while waiting for {licdebug_file}"
                " to exist."
            )

    with open(licdebug_file) as fid:
        # Going to the end of the file.
        if not debug:  # pragma: no cover
            fid.seek(0, 2)
        while True:
            lines = "".join(fid.readlines())
            yield lines


def get_ansys_license_directory():  # pragma: no cover
    """Get the path to the Ansys license directory"""

    # it's possible the user has specified the license as an env var
    ansyslic_dir = None
    if LIC_FILE_ENVAR in os.environ:
        ansyslmd_var = os.environ[LIC_FILE_ENVAR]
        if not os.path.isfile(ansyslmd_var):
            # likely license info
            ansyslic_dir = None
    else:
        ansyslic_dir = os.getenv(LIC_PATH_ENVAR)

    # env var may not be specified, check in the usual location
    if ansyslic_dir is None:
        if os.name == "nt":  # pragma: no cover
            ansyslic_dir = os.path.join(
                os.environ["ProgramFiles"],
                "ANSYS Inc",
                "Shared Files",
                "Licensing",
            )
        else:
            ansyslic_dir = "/usr/ansys_inc/shared_files/licensing"

        if not os.path.isdir(ansyslic_dir):
            raise FileNotFoundError(
                f"Unable to locate ANSYS licencing path at {ansyslic_dir}\n"
                f"Specify the {LIC_PATH_ENVAR}"
            )

    return ansyslic_dir


def get_ansys_license_debug_file_name():  # pragma: no cover
    """Get license client log file name.

    This file change the name according to the ANSYS version and the type of license requested (``$appname``).
    * For ANSYS version 22.1 and above: ``licdebug.$hostname.$appname.$version.out``
    * For ANSYS version 21.2 and below: ``licdebug.$appname.$version.out``

    where:
    * ``$hostname`` is the name of the machine.
    * ``$appname`` is the name of the feature used by the license client. Eg. 'FEAT_ANSYS'
    * ``$version`` is the version of ANSYS. Eg 211 for version 21.1.

    Returns
    -------
    str
        licdebug log file complete name.

    """
    # Licdebug name convention:
    # - For version 22.1 and above: `licdebug.$hostname.$appname.$version.out`
    # - For version 21.2 and below: `licdebug.$appname.$version.out`

    name = "licdebug"
    hostname = socket.gethostname()
    appname = APP_NAME
    # This is the type of license my client requests (Windows 10, 2021R2)
    version = version_from_path("mapdl", get_mapdl_path(allow_input=False))
    ending = "out"

    if version < 221:
        parts = (name, appname, version, ending)
    else:
        parts = (name, hostname, appname, version, ending)

    return ".".join([str(each_part) for each_part in parts])


def get_ansys_license_debug_file_path():  # pragma: no cover
    """Get license client log (``licdebug``) path.

    This path is obtained from the correspondent env variable (OS
    dependent) and appending ``.ansys``.

    Returns
    -------
    str
        path of the license client log file.
    """
    if os.name == "nt":
        folder = os.getenv("TEMP")
    elif os.name == "posix":
        folder = os.getenv("HOME")
    else:
        raise OSError(f"Unsupported OS {os.name}")

    return os.path.join(folder, ".ansys")


def get_ansys_license_utility_path():  # pragma: no cover
    """Return the ansys licencing utilities path."""
    ansyslic_dir = get_ansys_license_directory()
    if os.name == "nt":
        ansysli_util_path = os.path.join(ansyslic_dir, "winx64", "ansysli_util.exe")
    else:
        ansysli_util_path = os.path.join(ansyslic_dir, "linx64", "ansysli_util")

    return ansysli_util_path
