'''
Created on Oct 14, 2010

@author: jpg

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

Implements MCEliteError. 
Primarily used to get error feedback for ArcMap interface 
and propagate error messages up object hierarchy.

'''

class MCEliteError(Exception):
    '''
    Exception class for passing error messages to the 
    various front-ends that access MCElite. 
    '''
    pass
        