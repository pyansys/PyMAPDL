# Copyright (C) 2016 - 2024 ANSYS, Inc. and/or its affiliates.
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


class SolutionStatus:
    def atype(self, **kwargs):
        """Specifies "Analysis types" as the subsequent status topic.

        APDL Command: ATYPE

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
        command = f"ATYPE,"
        return self.run(command, **kwargs)

    def bioopt(self, **kwargs):
        """Specifies "Biot-Savart options" as the subsequent status topic.

        APDL Command: BIOOPT

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
        command = f"BIOOPT,"
        return self.run(command, **kwargs)

    def deact(self, **kwargs):
        """Specifies "Element birth and death" as the subsequent status topic.

        APDL Command: DEACT

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
        command = f"DEACT,"
        return self.run(command, **kwargs)

    def dynopt(self, **kwargs):
        """Specifies "Dynamic analysis options" as the subsequent status topic.

        APDL Command: DYNOPT

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
        command = f"DYNOPT,"
        return self.run(command, **kwargs)

    def gap(self, **kwargs):
        """Specifies "mode-superposition transient gap conditions" as the

        APDL Command: GAP
        subsequent status topic.

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
        command = f"GAP,"
        return self.run(command, **kwargs)

    def genopt(self, **kwargs):
        """Specifies "General options" as the subsequent status topic.

        APDL Command: GENOPT

        Notes
        -----
        This is a status (STAT) topic command. Status topic commands are
        generated by the GUI and will appear in the log file (Jobname.LOG) if
        status is requested for some items under Utility Menu> List> Status.
        This command will be immediately followed by a STAT command, which will
        report the status for the specified topic.

        If entered directly into the program, the STAT command should
        immediately follow this command.
        """
        command = f"GENOPT,"
        return self.run(command, **kwargs)

    def inrtia(self, **kwargs):
        """Specifies "Inertial loads" as the subsequent status topic.

        APDL Command: INRTIA

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
        command = f"INRTIA,"
        return self.run(command, **kwargs)

    def lsoper(self, **kwargs):
        """Specifies "Load step operations" as the subsequent status topic.

        APDL Command: LSOPER

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
        command = f"LSOPER,"
        return self.run(command, **kwargs)

    def master(self, **kwargs):
        """Specifies "Master DOF" as the subsequent status topic.

        APDL Command: MASTER

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
        command = f"MASTER,"
        return self.run(command, **kwargs)

    def nlopt(self, **kwargs):
        """Specifies "Nonlinear analysis options" as the subsequent status topic.

        APDL Command: NLOPT

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
        command = f"NLOPT,"
        return self.run(command, **kwargs)

    def outopt(self, **kwargs):
        """Specifies "Output options" as the subsequent status topic.

        APDL Command: OUTOPT

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
        command = f"OUTOPT,"
        return self.run(command, **kwargs)

    def smbody(self, **kwargs):
        """Specifies "Body loads on the solid model" as the subsequent status

        APDL Command: SMBODY
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
        command = f"SMBODY,"
        return self.run(command, **kwargs)

    def smcons(self, **kwargs):
        """Specifies "Constraints on the solid model" as the subsequent status

        APDL Command: SMCONS
        topic.

        Notes
        -----
        This is a status [STAT] topic command. Status topic commands are
        generated by the GUI and will appear in the log file (Jobname.LOG) if
        status is requested for some items under Utility Menu> List> Status.
        This command will be immediately followed by a STAT command, which will
        report the status for the specified topic.

        If entered directly into the program, the STAT command should
        immediately follow this command.
        """
        command = f"SMCONS,"
        return self.run(command, **kwargs)

    def smfor(self, **kwargs):
        """Specifies "Forces on the solid model" as the subsequent status topic.

        APDL Command: SMFOR

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
        command = f"SMFOR,"
        return self.run(command, **kwargs)

    def smsurf(self, **kwargs):
        """Specifies "Surface loads on the solid model" as the subsequent status

        APDL Command: SMSURF
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
        command = f"SMSURF,"
        return self.run(command, **kwargs)

    def soluopt(self, **kwargs):
        """Specifies "Solution options" as the subsequent status topic.

        APDL Command: SOLUOPT

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
        command = f"SOLUOPT,"
        return self.run(command, **kwargs)

    def sptopt(self, **kwargs):
        """Specifies "Spectrum analysis options" as the subsequent status topic.

        APDL Command: SPTOPT

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
        command = f"SPTOPT,"
        return self.run(command, **kwargs)
