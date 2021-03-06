'File: TestGPS.spin
CON
  _clkmode = xtal1 + pll16x
  _xinfreq = 5_000_000
  charDegree = $B0

OBJ
  Terminal: "FullDuplexSerial"
  Arduino: "FullDuplexSerial"
VAR
  byte Time[50]
	byte inByte
  byte fByte[4]
	long volt
PUB Start| fail,count,i,psize
  Terminal.start (31, 30, 0, 115200)
  Arduino.start (13, 0, 0, 9600) 'rx receive from arduino 
  Terminal.str (string ("Starting GPS "))
	SendString  (13) 'New Line
	'GPS.Start(13,12) 'rx - tx pins
	Terminal.str (string ("Waiting 42sec for GPS cold start "))
	SendString  (13) 'New Line
  'waitcnt (clkfreq*42 + cnt) 'delay 42s
  'Cold start need 42s, Warm 38s, Hot 8s
  waitcnt (clkfreq*2 + cnt) 'delay 2s
  repeat
		fail := false
		'The float serial protocol is send 'f',0,0,0,b1,b2,b3,b4
		inByte := Arduino.rxtime(1)
		
		if(inByte == 102)' char f
			psize := Arduino.rxtime(1)
			if(psize == 4)
				repeat i from 0 to psize-1
					fByte[i] := Arduino.rxtime(1)
					if(fByte[i] == 255)
						fail := true					
				if(fail <> true)
					volt := ((fByte[3]& $ff)<< 24)|((fByte[2] & $ff) << 16) | ((fByte[1] & $ff) << 8)|(fByte[0] & $ff)
    			Terminal.str (string ("Voltage: "))
					Terminal.dec(volt)
    			Terminal.str (string ("fByte:[ "))
					Terminal.dec(fByte[3])
    			Terminal.str (string ("][ "))
					Terminal.dec(fByte[2])
    			Terminal.str (string ("][ "))
					Terminal.dec(fByte[1])
    			Terminal.str (string ("][ "))
					Terminal.dec(fByte[0])
    			Terminal.str (string ("] "))
    			SendString  (13) 'New Line
				'else
    		'	Terminal.str (string ("Pack Time out: "))
    		'	SendString  (13) 'New Line
			else		
				Terminal.str (string ("Wrong Pack Size"))
				SendString  (13) 'New Line
			
		else
		
    		Terminal.str (string ("Got : "))
				Terminal.dec(inByte)
    		SendString  (13) 'New Line
PRI SendDecimal (DataIn)
  if DataIn == -1 'The data is set to -1 if invalid
    Terminal.str (string ("Invalid"))
  else
    Terminal.dec (DataIn)

PRI SendString (DataIn)
  if DataIn == -1 'The data is set to -1 if invalid
    Terminal.str (string ("Invalid"))
  else
    Terminal.tx (DataIn)

{PRI SendFloat2 (DataIn) 'Send hundreth of decimal
  if DataIn == -1
    Terminal.str (string ("Invalid"))
  elseif DataIn > 99 'overload error
    Terminal.str (string ("##"))
  elseif DataIn > 9  '0.10 ~ 0.99
    Terminal.dec (DataIn)
  elseif DataIn > 0  '0.01 ~ 0.09
    Terminal.str (string ("0"))
    Terminal.dec (DataIn)
  else 'Others, just send all 0s
    Terminal.str (string ("00"))

PRI SendFloat3 (DataIn) 'Send thousandth of decimal
  if DataIn == -1
    Terminal.str (string ("Invalid"))
  elseif DataIn > 999 'overload error
    Terminal.str (string ("###"))
  elseif DataIn > 99  '0.100 ~ 0.999
    Terminal.dec (DataIn)
  elseif DataIn > 9  '0.010 ~ 0.099
    Terminal.str (string ("0"))
    Terminal.dec (DataIn)
  elseif DataIn > 0  '0.001 ~ 0.009
    Terminal.str (string ("00"))
    Terminal.dec (DataIn)
  else 'Others, just send all 0s
    Terminal.str (string ("000"))

PRI SendFloat4 (DataIn) 'Send ten thousandth of decimal
  if DataIn == -1
    Terminal.str (string ("Invalid"))
  elseif DataIn > 9999 'overload error
    Terminal.str (string ("####"))
  elseif DataIn > 999 '0.1000 ~ 0.9999
    Terminal.dec (DataIn)
  elseif DataIn > 99  '0.0100 ~ 0.0999
    Terminal.str (string ("0"))
    Terminal.dec (DataIn)
  elseif DataIn > 9  '0.0010 ~ 0.0099
    Terminal.str (string ("00"))
    Terminal.dec (DataIn)
  elseif DataIn > 0  '0.0001 ~ 0.0009
    Terminal.str (string ("000"))
    Terminal.dec (DataIn)
  else 'Others, just send all 0s
    Terminal.str (string ("0000"))
}
PRI SendSign (DataIn)
  if DataIn == 0
    Terminal.tx (" ")
  elseif DataIn == 1
    Terminal.tx ("-")
  else
    Terminal.str (string ("Invalid"))
  
PRI PrecisionRating (DD,M)
  case DD
    -1,0:
        Terminal.str (string ("Invalid"))
    1:
      if M == 0
        Terminal.str (string ("Ideal"))
      else
        Terminal.str (string ("Excellent"))
    2,3,4:
        Terminal.str (string ("Good"))
    5,6,7,8,9:
        Terminal.str (string ("Moderate"))
    10,11,12,13,14,15,16,17,18,19:
        Terminal.str (string ("Fair"))
    20:
      if M == 0
        Terminal.str (string ("Fair"))
      else
        Terminal.str (string ("Poor"))
    other:
        Terminal.str (string ("Poor"))
    
  
  

'TODO: fix the naming
'      float --> fixed numbering
'      float2 means it will always transmit 2 digits
'TODO: the data are all integer-based for easy transmitting thru normal FullDuplexSerial
'      change to float-based
