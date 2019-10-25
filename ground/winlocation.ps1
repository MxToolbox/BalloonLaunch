Add-Type -AssemblyName System.Device #Required to access System.Device.Location namespace
$GeoWatcher = New-Object System.Device.Location.GeoCoordinateWatcher #Create the required object
$GeoWatcher.Start() #Begin resolving current locaton

while (($GeoWatcher.Status -ne 'Ready') -and ($GeoWatcher.Permission -ne 'Denied')) {
    Start-Sleep -Milliseconds 100 #Wait for discovery.
}  

while (1 -ne 2) {
    if ($GeoWatcher.Permission -eq 'Denied'){
        Write-Error 'Access Denied for Location Information'
    } else {
        $GeoWatcher.Position.Location  | Out-File  -Encoding "UTF8" .\location.txt # | Select Latitude,Longitude,Altitude #Select the relevent results.
    }
    Start-Sleep 5
}