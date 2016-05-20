<?php
$run = $argv[1];
$duration = $argv[2];
$time = date("r",time());
$headers = 'From: TerpWRF <no-reply@trowal.weather.umd.edu>';
$subject = 'The '.$run.'Z TerpWRF run has completed';
$message = 'TerpWRF has successfully completed its run initialized with the '.$run.'Z GFS run.'."\n";
$message .= 'Total time to completion: '.$duration." minutes\n";
$message .= 'Completion time: '.$time."\n";


#mail("help@sense.umd.edu", $subject, $message, $headers);
mail("cmart90@umd.edu",$subject,$message,$headers); // change this address later?
mail("dkleist@umd.edu",$subject,$message,$headers); // change this address later?
mail("tjarcomano@yahoo.com",$subject,$message,$headers); // change this address later?
?>
