#!/bin/bash

IDRAC_IP=""
USERNAME=""
PASSWORD=""

if [$IDRAC_IP == ""]; then
    echo.
    echo '>> !! Please setup the "modules/projects/idrac_power.sh" !!'
    exit
fi

case "$1" in
    on)
        ipmitool -I lanplus -H $IDRAC_IP -U $USERNAME -P $PASSWORD chassis power on
        ;;
    fan)
        case "$2" in
            10)
                speed=0x0A
                ;;
            15)
                speed=0x0F
                ;;
            20)
                speed=0x14
                ;;
            25)
                speed=0x19
                ;;
            30)
                speed=0x1E
                ;;
            35)
                speed=0x23
                ;;
            40)
                speed=0x28
                ;;
            45)
                speed=0x2D
                ;;
            50)
                speed=0x32
                ;;
            55)
                speed=0x37
                ;;
            60)
                speed=0x3C
                ;;
            *)
                echo "Usage: $0 $1 {10|15|20|25|30|35|40|45|50|55|60}"
                exit 1
                ;;
        esac
        ipmitool -I lanplus -H $IDRAC_IP -U $USERNAME -P $PASSWORD raw 0x30 0x30 0x01 0x00
        ipmitool -I lanplus -H $IDRAC_IP -U $USERNAME -P $PASSWORD raw 0x30 0x30 0x02 0xff $speed
        ;;
    off)
        ipmitool -I lanplus -H $IDRAC_IP -U $USERNAME -P $PASSWORD chassis power off
        ;;
    cycle)
        ipmitool -I lanplus -H $IDRAC_IP -U $USERNAME -P $PASSWORD chassis power cycle
        ;;
    status)
        ipmitool -I lanplus -H $IDRAC_IP -U $USERNAME -P $PASSWORD chassis status
        ;;
    *)
        echo "Usage: $0 {on|off|fan|cycle|status}"
        exit 1
        ;;
esac
