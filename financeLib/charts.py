#!/usr/bin/env python3
# charts.py
# library to create charts

from flask import Markup

def createLineGraph(lname, name, values):

	string =  'var ' + name + ' = new CanvasJS.Chart("' + name + 'Container",{'
	string += '	title:{'
	string += '		text: "' + lname + '"'
	string += '	},'
	string += '	axisX:{'
	string += '		gridThickness: 2, '
	string += '		interval: 5,'
	string += '		labelAngle: -45'
	string += '	},'
	string += '	axisY:{'
	string += '		valueFormatString: "#,##0.####",'
	string += '		suffix: "%",'
	string += '	},'
	string += '	data: [{'
	string += '		type: "line",'
	string += '		dataPoints: ['

	for x in range(len(values)):
		string += '		{ x: new Date(2016,0,1,6,30+' + str(x) + ',0,0), y: ' + str(values[x]) + ' },'

	string += '		]'
	string += '	}]'
	string += '});'
	string += '' + name + '.render();'
	string += '' + name + ' = {};'

	returnstring = Markup(string)

	return returnstring
	
def displayLineGraph(name):

	string = '<div id="' + name + 'Container" style="height: 300px; widthh: 100%;"></div>'

	returnstring = Markup(string)

	return returnstring	

#	print('<div id="' + name + 'Container" style="height: 300px; width: 100%;"></div>')




