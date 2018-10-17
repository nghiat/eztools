::----------------------------------------------------------------------------::
:: ezdeps.bat                                                                 ::
::                                                                            ::
:: This file is distributed under the MIT License.                            ::
:: See LICENSE.txt for details.                                               ::
:: Copyright (C) Tran Tuan Nghia <trantuannghia95@gmail.com> 2018             ::
::----------------------------------------------------------------------------::
@echo off

py -3 "%~dp0\eztools.py" --tool=ezdeps %*
