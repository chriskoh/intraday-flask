#!/usr/bin/env python3
# charts.py
# library to create charts

import cgi
import cgitb
cgitb.enable()

def createLineGraph(lname, name, values):
	
	print('var ' + name + ' = new CanvasJS.Chart("' + name + 'Container",{')
	print('	title:{')
	print('		text: "' + lname + '"')
	print('	},')
	print('	axisX:{')
	print('		gridThickness: 2,')
	print('		interval:5, ')
	print('		labelAngle: -45')
	print('	},')
	print('	axisY:{')
	print('		valueFormatString:  "#,##0.####",')
	print('		suffix: "%",')
	print('	},')
	print('	data: [{')
	print('		type: "line",')
	print('		dataPoints: [')
	for x in range(len(values)):
		print('		{ x: new Date(2016,0,1,6,30+' + str(x) + ',0,0), y: ' + str(values[x]) + ' },') # date does not matter, only time will be displayed
	print('		]')
	print('	}]')
	print('});')
	print('' + name + '.render();')
	print('' + name + ' = {};')
	
def displayLineGraph(name):
	
	print('<div id="' + name + 'Container" style="height: 300px; width: 100%;"></div>')
