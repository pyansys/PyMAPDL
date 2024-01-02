# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
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

class Status:
    def calc(self, **kwargs):
        """Specifies "Calculation settings" as the subsequent status topic.

        APDL Command: CALC

        Notes
        -----
        This is a status [STAT] topic command.  Status topic commands are
        generated by the GUI and will appear in the log file (Jobname.LOG) if
        status is requested for some items under Utility Menu> List> Status.
        This command will be immediately followed by a STAT command, which will
        report the status for the specified topic.

        If entered directly into the program, the STAT command should
        immediately follow this command.
        """
        command = f"CALC,"
        return self.run(command, **kwargs)

    def datadef(self, **kwargs):
        """Specifies "Directly defined data status" as the subsequent status

        APDL Command: DATADEF
        topic.

        Notes
        -----
        This is a status [STAT] topic command.  Status topic commands are
        generated by the GUI and will appear in the log file (Jobname.LOG) if
        status is requested for some items under Utility Menu> List> Status.
        This command will be immediately followed by a STAT command, which will
        report the status for the specified topic.

        If entered directly into the program, the STAT command should
        immediately follow this command.
        """
        command = f"DATADEF,"
        return self.run(command, **kwargs)

    def display(self, **kwargs):
        """Specifies "Display settings" as the subsequent status topic.

        APDL Command: DISPLAY

        Notes
        -----
        This is a status [STAT] topic command.  Status topic commands are
        generated by the GUI and will appear in the log file (Jobname.LOG) if
        status is requested for some items under Utility Menu> List> Status.
        This command will be immediately followed by a STAT command, which will
        report the status for the specified topic.

        If entered directly into the program, the STAT command should
        immediately follow this command.
        """
        command = f"DISPLAY,"
        return self.run(command, **kwargs)

    def lccalc(self, **kwargs):
        """Specifies "Load case settings" as the subsequent status topic.

        APDL Command: LCCALC

        Notes
        -----
        This is a status [STAT] topic command.  Status topic commands are
        generated by the GUI and will appear in the log file (Jobname.LOG) if
        status is requested for some items under Utility Menu> List> Status.
        This command will be immediately followed by a STAT command, which will
        report the status for the specified topic.

        If entered directly into the program, the STAT command should
        immediately follow this command.

        This command is also valid for rezoning.
        """
        command = f"LCCALC,"
        return self.run(command, **kwargs)

    def point(self, **kwargs):
        """Specifies "Point flow tracing settings" as the subsequent status topic.

        APDL Command: POINT

        Notes
        -----
        This is a status [STAT] topic command.  Status topic commands are
        generated by the GUI and will appear in the log file (Jobname.LOG) if
        status is requested for some items under Utility Menu> List> Status.
        This command will be immediately followed by a STAT command, which will
        report the status for the specified topic.

        If entered directly into the program, the STAT command should
        immediately follow this command.
        """
        command = f"POINT,"
        return self.run(command, **kwargs)

    def spec(self, **kwargs):
        """Specifies "Miscellaneous specifications" as the subsequent status

        APDL Command: SPEC
        topic.

        Notes
        -----
        This is a status [STAT] topic command.  Status topic commands are
        generated by the GUI and will appear in the log file (Jobname.LOG) if
        status is requested for some items under Utility Menu> List> Status.
        This command will be immediately followed by a STAT command, which will
        report the status for the specified topic.

        If entered directly into the program, the STAT command should
        immediately follow this command.
        """
        command = f"SPEC,"
        return self.run(command, **kwargs)
