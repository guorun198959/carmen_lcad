CON
  _clkmode = xtal1 + pll16x ' System clock → 80 MHz
  _xinfreq = 5_000_000
  
OBJ
  serial           : "FullDuplexSerial"

PUB Main | cmd, pinState, data, dataHigh, dataLow
  
  'Start the serial
  serial.start(31, 30, 0, 115200)

  'Setup the pin for the manipulator enable
  dira[0] := 1   'DATA1 to robot
  dira[1] := 1   'DATA2 to robot
  dira[2] := 1   'DATA3 to robot
  dira[3] := 1   'DATA4 to robot
  dira[4] := 1   'DATA5 to robot
  dira[5] := 1   'CLOCK to robot 
  dira[6] := 0   'BUSY signal from robot
  dira[7] := 0   'HOME signal from robot

  dira[16] := 1  'LED   
  dira[17] := 1  'LED   
  dira[18] := 1  'LED   

	outa[0] := 1 
	outa[1] := 1
	outa[2] := 1
	outa[3] := 1
	outa[4] := 1
	outa[5] := 1
	outa[6] := 1


  repeat
    cmd := serial.rxcheck

    outa[16] := 1
		waitcnt(10_000_000 + cnt)
		outa[16] := 0
		waitcnt(10_000_000 + cnt)


    case cmd

			'##############################
			"B": 'get BUSY state
				outa[16] := !outa[16]
				pinState := ina[6]
				if (pinState == 0)
					serial.str(string("1")) 
				else
					serial.str(string("0")) 

			'##############################
			"H": 'get HOME state
				outa[17] := !outa[17]
				pinState := ina[7]
				if (pinState == 0)
					serial.str(string("1")) 
				else
					serial.str(string("0")) 
			
			'##############################
			"P": 'Execute Path 
				outa[18] := !outa[18]

				'Get the position number
				data := serial.rx

				'Set the data lines (active low)
				data := !data
				outa := (data & $1F)

				'Clock the data in
				outa[5] := 0 
				waitcnt(90_000_000 + cnt)
				outa[5] := 1  

			'##############################
			"Q": 'Execute Path (Human input for debugging)
				outa[18] := !outa[18]

				'Get the high and low digits as ascii 
				' (e.g. 03, 18, 31, etc..)
				dataHigh := serial.rx
				dataLow := serial.rx
				data := (dataHigh-48)*10 + (dataLow-48)

				'Set the data lines (active low)
				data := !data
				outa := (data & $1F)

				'Clock the data in
				outa[5] := 0 
				waitcnt(180_000_000 + cnt)
				outa[5] := 1  
