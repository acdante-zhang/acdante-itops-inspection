#!/bin/bash
#Auditor Name:TianYi Acdante
export LANG="C"
export LANG_ALL="C"
export E="echo"
Usage()
{
 $E ""
 $E "Syntax"
 $E ""
 $E "       [ -v ] [ -h | -? ] [ -f LOGName ] [ { -gets | -skip } ItemName ... ]"
 $E ""
 $E "Description"
 $E ""
 $E "       This shell script collection of OS,LVM,STORAGE,PERFORMANCE,NETWORK,RHCS,LOG,ORACLE,STORAGE FOUNDATION,NETBACKUP information."
 $E ""
 $E "       Default collect all the information,but use flags to collect the information you need. after information is collected, through the FTP download it."
 $E ""
 $E "       \"-f\" and \"-gets\" or \"-skip\" flags can be used together, but \"-gets\" and \"-skip\" flags cannot be used together."
 $E ""
 $E "Flags"
 $E ""
 $E "       -v version"
 $E "            Show script version and exit."
 $E ""
 $E "       -f file"
 $E "            Write html output to specified file."
 $E "            If you do not specify an absolute path, the default output to the /tmp directory."
 $E ""
 $E "       -gets"
 $E "            Collect information for given item only,specify items as a comma-separated list."
 $E "            Options: os,lvm,sto,per,net,ha,log,ora,sf,nbu,the default is all items."
 $E ""
 $E "       -skip"
 $E "            Collect all the information except specified items,specify items as a comma-separated list."
 $E "            Options: os,lvm,sto,per,net,ha,log,ora,sf,nbu,the default is no items."
 $E ""
 $E "       -h|-? help"
 $E "            Show help screen."
 $E ""
 $E "Examples"
 $E ""
 $E "       1    Collect all the System information:"
 $E "            ./Sysinfo_$Version.sh"
 $E ""
 $E "       2    Collect information for lvm and oracle:"
 $E "            ./Sysinfo_$Version.sh -gets lvm,ora"
 $E ""
 $E "       3    Collect all the information except storage foundation and lvm:"
 $E "            ./Sysinfo_$Version.sh -skip sf,lvm"
 $E ""
 $E "       4    Write output infomation to \"/tmp/test\" or \"/opt/20211108.html\":"
 $E "            ./Sysinfo_$Version.sh -f test"
 $E "            ./Sysinfo_$Version.sh -f /opt/20211108.html"
 $E ""
 exit 0
}
CHK_PRM(){ CHK_OS=$1;CHK_LVM=$1;CHK_STO=$1;CHK_PER=$1;CHK_NET=$1;CHK_HA=$1;CHK_LOG=$1;CHK_ORA=$1;CHK_SF=$1;CHK_NBU=$1;}
P_ERR_CHR()
{
 charlen=`expr length "$1"`;((charlen=charlen+3))
 while [[ $charlen > 0 ]];do ((charlen=charlen-1));$E -n '*';done
 $E '*'
}
P_ERR(){ $E "";P_ERR_CHR "$1";$E -n '*';$E -n " $1 ";$E '*';P_ERR_CHR "$1";$E "";}
P_MARK()
{
 if [[ -n "$2" ]];then marklen=$2
 else marklen=$LOGLen;[[ $marklen -lt 45 ]] && marklen=45
 fi
 while [[ $marklen > 1 ]];do ((marklen=marklen-1));$E -n "$1";done
 $E "$1"
}
PP(){ P_MARK "$1" "$2">>$LOG 2>&1;}
PWD()
{
 TIANYIm=$(date +%m);TIANYId=$(date +%d);err=3
 while [[ $err > 0 ]];do
	stty -$E;$E -n "Enter Password: ";read password
	if [[ "$password" != "tyyj$TIANYIm$TIANYId" ]];then ((err=err-1));P_ERR "You entered an invalid login password";stty $E
	else stty $E;break;fi
 done
 if [[ $err -eq 0 ]];then P_ERR "Password is entered incorrectly too many times";exit;fi
 $E ""
}
INFO_CHK()
{
 if [[ -n "$INFO_N_CHK" ]];then
	if [[ -n "$CHK" ]];then P_ERR "\"-gets\" and \"-skip\" cannot be used together,please refer to the help.";exit 0
	else
	 CHK="Y";CHK_PRM "Y";CHKD=0
	 for No_CheckItem in $INFO_N_CHK;do
		((CHKD=CHKD+1))
		case $No_CheckItem in
		 os) CHK_OS="N";;
		 lvm) CHK_LVM="N";;
		 sto) CHK_STO="N";;
		 per) CHK_PER="N";;
		 net) CHK_NET="N";;
		 ha) CHK_HA="N";;
		 log) CHK_LOG="N";;
		 ora) CHK_ORA="N";;
		 sf) CHK_SF="N";;
		 nbu) CHK_NBU="N";;
		 *) P_ERR "\"$No_CheckItem\" parameter is invalid,please refer to the help.";exit 0;;
		esac
	 done
	 if [[ $CHKD -eq 10 ]];then P_ERR "Warning: All items are excluded,the program will exit.";exit 0;fi
	fi
 fi
 if [[ -n "$INFO_CHK" ]];then
	if [[ -n "$CHK" ]];then P_ERR "\"-gets\" and \"-skip\" cannot be used together,please refer to the help.";exit 0
	else
	 CHK="Y";CHK_PRM "N"
	 for CheckItem in $INFO_CHK;do
		case $CheckItem in
		 os) CHK_OS="Y";;
		 lvm) CHK_LVM="Y";;
		 sto) CHK_STO="Y";;
		 per) CHK_PER="Y";;
		 net) CHK_NET="Y";;
		 ha) CHK_HA="Y";;
		 log) CHK_LOG="Y";;
		 ora) CHK_ORA="Y";;
		 sf) CHK_SF="Y";;
		 nbu) CHK_NBU="Y";;
		 *) P_ERR "\"$CheckItem\" parameter is invalid,please refer to the help.";exit 0;;
		esac
	 done
	fi
 fi
}
ParseCommandline ()
{
 if [[ -n "$5" ]];then P_ERR "ERROR: Too many arguments,please refer to the help!";exit 0
 else
	while [[ $# -ne 0 ]];do
	 case $1 in
	 -v) $E $Version;exit 0;;
	 -f)
		shift
		if [[ -z "$($E $1)" ]];then P_ERR "ERROR: Please specify the output file name!";exit 0
		else
		 $E "$($E $1)"|grep -q "/"
		 if [[ $? -eq 0 ]];then LOG=$($E $1);else LOG=$LogPath/$($E $1);fi
		 if [[ -e $LOG ]];then P_ERR "ERROR: Specify the file \"$LOG\" already exists,please check!";exit 0;fi
		fi;;
	 -skip)
		shift
		if [[ -z "$($E $1)" ]];then P_ERR "ERROR: Please specify the excluded items!";exit 0;else INFO_N_CHK=$($E $1|sed 's/,/ /g');fi;;
	 -gets)
		shift
		if [[ -z "$($E $1)" ]];then P_ERR "ERROR: Please specify the need to collect items!";exit 0;else INFO_CHK=$($E $1|sed 's/,/ /g');fi;;
	 -h|-?|-*help) Usage;;
	 *) P_ERR "ERROR: unrecognized option \"$1\"";Usage;;
	 esac
	 shift
	done
 fi
}
RM(){ [[ -f $1 ]] && rm -fr $1 2>&1;}
if [[ `whoami` != "root" ]];then P_ERR "WARNING: Please run this script as user root.";exit 0;fi
umask 022;Draw_hr=0;Version=V2.1;LogPath=/tmp
HostName=`hostname||uname -n`;Time=`date +20%y%m%d%H%M`
CHK_PRM "Y";ParseCommandline $*
INFO_CHK
PWD
SerialNum=`dmidecode -s system-serial-number`
if [[ -f /tmp/Sysinfo_Client_IP ]];then Logon_IP=`cat /tmp/Sysinfo_Client_IP`;RM "/tmp/Sysinfo_Client_IP";else Logon_IP=`who am i|awk '{print $NF}'|sed -e 's/(//g' -e 's/)//g'`;fi
ip_count=0
for IP in `ifconfig|grep 'inet addr:'|grep -v '127.0.0.1'|cut -d: -f2|awk '{print $1}'`;do ips[$ip_count]=$IP;((ip_count+=1));done
if [[ $ip_count -eq 1 ]];then IP_Addr=${ips[0]}
else
 ((ip_count1=ip_count-1))
 for ((i=0;i<ip_count;i=i+1));do
	IP_Addr+=${ips[$i]}
	[[ $i -lt $ip_count1 ]] && IP_Addr+=" | "
 done
fi
[[ -f /tmp/Sysinfo_IP ]] && ips[0]=`cat /tmp/Sysinfo_IP`
LogName=Sysinfo_${HostName}_${ips[0]}_$Time.html
[[ -z "$LOG" ]] && LOG=$LogPath/${LogName}
if [[ -f /tmp/Sysinfo_IP ]];then echo $LOG>/tmp/${ips[0]}_Log_Name 2>&1;RM "/tmp/Sysinfo_IP";fi
((LOGLen=`expr length "$LOG"`+20))
$E ""
P_MARK "="
$E "Sysinfo Version $Version by TianYi"
$E ""
$E "Server  : ${HostName}"
$E "Started : `date`"
P_MARK "="
$E "Initializing...."
STARTH=$(date +%H);TIANYIm=$(date +%M);STARTS=$(date +%S)
Type=`dmidecode -t1|grep "Product Name"|awk 'BEGIN {FS=": "}{print $2}'`

OSVersion=N/A
[[ -x /usr/bin/lsb_release ]] && OSVersion=`lsb_release -ds|sed 's/"//g'`
KernelVersion=`uname -ri`
Date=`date +20%y-%m-%d`
UpdateTime=2022-01-20
if [[ `uptime|grep days` ]];then UPTime=`uptime|awk '{print $3$4$5}'|awk 'BEGIN {FS=","}{print $1" "$2}'`;else UPTime=`uptime|awk '{print $3}'|awk 'BEGIN {FS=","}{print $1}'`;fi
if [[ -f /etc/lsb-release ]];then
 [[ -n `cat /etc/lsb-release|grep Ubuntu >/dev/null` ]] && UBUNTU="Y"
fi
[[ -f /etc/SuSE-release ]] && SUSE="Y"
if [[ "$UBUNTU" = "Y" ]];then DefRunLevel=`cat /etc/init/rc-sysinit.conf|grep "env DEFAULT_RUNLEVEL"|awk '{print $2}'`;else [[ -r /etc/inittab ]] && DefRunLevel=`awk '!/#|^ *$/ && /initdefault/' /etc/inittab`;fi
CurRunLevel=`/sbin/runlevel`
if [[ "$SUSE" = "Y" ]];then InstallTime=`passwd -S bin|awk '{print $3}'`
else
 for sd in `fdisk -l 2>&1|grep /dev/sda|grep -v Disk|grep -v swap|grep -v Extended|grep -v grep|awk '{print $1}'`;do
	InstallTime=`tune2fs -l $sd|grep "Filesystem created"|awk 'BEGIN {FS=": "}{print $2}'|sed 's/^ *\| *$//g'`
	[[ -n $InstallTime ]] && break;
 done
fi
if [[ ! -e $LogPath ]];then mkdir $LogPath;cd $LogPath;chmod o+w $LogPath;else cd $LogPath;fi
touch $LOG
cmd(){ if [[ -n "$2" ]];then
 if [[ -n `$1 2>&1` ]];then $1>>$LOG 2>&1;else P;fi
else $1>>$LOG 2>&1;fi;}
EE(){ $E $1>>$LOG 2>&1;}
$E '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html><head><meta http-equiv="Content-Type" content="text/html;charset=gb2312">'>$LOG 2>&1
if [[ -n `$E ${ips[0]}` ]];then EE "<title>LINUX系统信息-${ips[0]}</title>";else EE "<title>LINUX系统信息</title>";fi
$E '
<style type="text/css" id="white" disabled="ture">
li{font-family:Arial,Helvetica,verdana,sans-serif;list-style:none;background-repeat:no-repeat;}
pre{white-space:pre-wrap;white-space:-moz-pre-wrap;white-space:-pre-wrap;white-space:-o-pre-wrap;word-wrap:break-word;}
a{text-decoration:none;}
a:hover{text-decoration:none;}
.coltable{border:thin black solid;}
.tabletitle{font-family:Arial,Helvetica,verdana,sans-serif;font-size:medium;font-weight:bold;color:#000000;}
.tableheader {background-color:#A8A8A8;color:#000000;height:28px;font:10.5pt sans-serif,Arial,Helvetica;padding-left:20px;text-align:left;}
.bg0 {background-color:#E4E4E4;text-align:left;height:28px;}
.bg1 {background-color:#F5F7F7;text-align:left;height:28px;}
td.tabtop {font-size:x-small;text-align:left;font:10.5pt Arial,Helvetica,sans-serif;color:#004B8B;background:#E2E6E7;padding-left:8px;line-height:18pt}
body,div{margin:0;padding:0;}
.top{background:#000000;height:55px;}
.left{background:#F5F7F7;position:absolute;width:220px;text-align:left;top:55px;bottom:0;overflow:auto;}
.main{background:#CCCCCC;position:absolute;left:220px;right:0;top:55px;bottom:0;overflow:auto;padding-left:10px;}
div.sdmenu{width:360px;font-size:14px;font-weight:bold;color:#000000;}
div.sdmenu div{overflow:hidden;}
div.sdmenu div.collapsed {height:26px;}
div.sdmenu div span {display:block;line-height:26px;width:360px;font-weight:bold;color:#004B8B;cursor:pointer;margin-left:6px;}
div.sdmenu div span a{padding:0;background:none;border:0;font-size:14px;line-height:26px;display:block}
div.sdmenu div.collapsed {width:360px;color:#000000}
div.sdmenu div.collapsed span{color:#000000;line-height:26px}
div.sdmenu div.collapsed span a.current{color:#000000;}
div.sdmenu div a {padding-left:12px;display:block;border-bottom:1px solid #FFFFFF;color:#1F1F1F;font-size:14px;font-weight:lighter;background:#E8E8E8;line-height:26px}
div.sdmenu div a.current {background:#C8C8C8;color:#000000;font-weight:bold;}
div.sdmenu div a:hover {background:#D8D8D8;color:#000000;text-decoration:none;}
div.sdmenu div span a.current {background:none;color:#004B8B}
div.sdmenu div span a:hover {background:none;}
table,td,th{font-size:14px;padding:0px 0px 0px 0px;margin:0px 0px 0px 0px;}
.tab1{background-color:#CCCCCC;border:0;width:800px;height:100%;text-align:left;}
.cmdtab{border:0;width:1220px;text-align:left;background-color:#E2E6E7}
.hr1{height:2px;width:1220px;border-width:0;color:#606060;background-color:#606060;}
.bothr{height:2px;width:1220px;border-width:0;color:#DEDEDE;background-color:#DEDEDE;}
.result{border:0;width:1220px;text-align:left;background-color:#F5F7F7}
.td1{color:#000000;}
.td2{word-wrap:break-word;word-break:break-all;}
.td3{padding-left:20px;}
.ft1{color:#0000BF;}
#colordiv{position:fixed;bottom:20px;right:20px;width:120px;height:28px;background-color:#6E6E6E;border:1px solid #000000;color:#FFFFFF;line-height:28px;padding-left:8px;font-size:14px;font-weight:bold;}
.tabwhite{background-color:#F3F3F3;width:14px;height:14px;cursor:pointer;overflow:hidden;border:1px solid #000000;}
.tabblack{background-color:#87CEEB;width:12px;height:12px;cursor:pointer;overflow:hidden;border:0px;}
div.sdmenu li:hover{padding-left:8px;background-image: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAMAAAAaCAYAAABy8ebsAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8
YQUAAAAJcEhZcwAAEnQAABJ0Ad5mH3gAAAAjSURBVChTYzz19Pl/BihggtJgMMohnnPl+UuGP//+AZkMDAAHIwllhctJnwAAAABJRU5ErkJ
ggvHHT7FKomMG77lL/iev2vC/dtf+/zNOnv2/+cZtrApPPX3+HwDLkGCyfHNDwwAAAABJRU5ErkJggg==");}
div.sdmenu li:active{color:#E74C3C;padding-left:8px;background-image: url("data:image/png;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQECAQEBAQEBAgICAgICAgICAgICAgICAgICAgICAgICAgICAgL/2wBDAQEBAQEBAQICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgL/wAARCAAaAAMDAREAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAb/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFgEBAQEAAAAAAAAAAAAAAAAAAAkK/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8Ah072ngAAB//Z");}
</style>
<style type="text/css" id="black" disabled="false">
li{font-family:Arial,Helvetica,verdana,sans-serif;list-style:none;background-repeat:no-repeat;}
pre{white-space:pre-wrap;white-space:-moz-pre-wrap;white-space:-pre-wrap;white-space:-o-pre-wrap;word-wrap:break-word;}
a{text-decoration:none;}
a:hover{text-decoration:none;}
.coltable{border:thin black solid;}
.tabletitle{font-family:Arial,Helvetica,verdana,sans-serif;font-size:medium;font-weight:bold;color:white;}
.tablesubtitle{font-family:Arial,Helvetica,verdana,sans-serif;font-size:small;font-weight:bold;color:white;}
.tableheader {background-color:#87CEEB;color:white;height:28px;font:10.5pt sans-serif,Arial,Helvetica;padding-left:20px;text-align:left;}
.bg0{background-color:#CCCCCC;text-align:left;height:28px;}
.bg1{background-color:#BBBBBB;text-align:left;height:28px;}
td.tabtop{font-size:x-small;text-align:left;font:10.5pt Arial,Helvetica,sans-serif;color:#FFFFFF;background:#87CEEB;padding-left:8px;line-height:18pt}
body,div{margin:0;padding:0;}
.top{background:#000000;height:55px;}
.left{background:#000000;position:absolute;width:220px;text-align:left;top:55px;bottom:0;overflow:auto;}
.main{background:#444444;position:absolute;left:220px;right:0;top:55px;bottom:0;overflow:auto;padding-left:10px;}
div.sdmenu{width:360px;font-size:14px;font-weight:bold;color:white;}
div.sdmenu div{overflow:hidden;}
div.sdmenu div.collapsed {height:26px;}
div.sdmenu div span {display:block;line-height:26px;width:360px;font-weight:bold;color:#BF0000;cursor:pointer;margin-left:6px;}
div.sdmenu div span a{padding:0;background:none;border:0;font-size:14px;line-height:26px;display:block}
div.sdmenu div.collapsed {width:360px;color:white}
div.sdmenu div.collapsed span{color:white;line-height:26px}
div.sdmenu div.collapsed span a.current{color:white;}
div.sdmenu div a {padding-left:12px;display:block;border-bottom:1px solid #000000;color:#D6D6D6;font-size:14px;font-weight:lighter;background:#87CEEB;line-height:26px}
div.sdmenu div a.current {background:#593019;color:#FFFFFF;font-weight:bold;}
div.sdmenu div a:hover {background:#1F1F1F;color:#FFFFFF;text-decoration:none;}
div.sdmenu div span a.current {background:none;color:#BF0000}
div.sdmenu div span a:hover {background:none;}
table,td,th{font-size:14px;padding:0px 0px 0px 0px;margin:0px 0px 0px 0px;}
.tab1{border:0;width:800px;height:100%;color:#000000;background-color:#444444;text-align:left;}
.cmdtab{border:0;width:1220px;text-align:left;background-color:#87CEEB}
.hr1{height:2px;width:1220px;border-width:0;color:#FFFFFF;background-color:#FFFFFF;}
.bothr{height:2px;width:1220px;border-width:0;color:#808080;background-color:#808080;}
.result{border:0;width:1220px;text-align:left;background-color:#BBBBBB}
.td1{color:#E7FBFF;}
.td2{word-wrap:break-word;word-break:break-all;}
.td3{padding-left:20px;}
.ft1{color:#FE4F23;}
#colordiv{position:fixed;bottom:20px;right:20px;width:120px;height:28px;background-color:#6E6E6E;border:1px solid #FFFFFF;color:#000000;line-height:28px;padding-left:8px;font-size:14px;font-weight:bold;}
.tabwhite{background-color:#F3F3F3;width:12px;height:12px;cursor:pointer;overflow:hidden;border:0px;}
.tabblack{background-color:#87CEEB;width:14px;height:14px;cursor:pointer;overflow:hidden;border:1px solid #FFFFFF;}
div.sdmenu li:hover{padding-left:8px;background-image: url("data:image/png;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQECAQEBAQEBAgICAgICAgICAgICAgICAgICAgICAgICAgICAgL/2wBDAQEBAQEBAQICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgL/wAARCAAaAAMDAREAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAr/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFAEBAAAAAAAAAAAAAAAAAAAAAP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AL+AAAAf/9k=");}
div.sdmenu li:active{color:#E74C3C;padding-left:8px;background-image: url("data:image/png;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQECAQEBAQEBAgICAgICAgICAgICAgICAgICAgICAgICAgICAgL/2wBDAQEBAQEBAQICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgL/wAARCAAaAAMDAREAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAb/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFgEBAQEAAAAAAAAAAAAAAAAAAAkK/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8Ah072ngAAB//Z");}
</style></head><body style="overflow:hidden;">'>>$LOG 2>&1
$E '<SCRIPT type=text/javascript>
function closewin()
{
 window.opener=null;
 window.open("","_self");
 window.close();
}
if(navigator.userAgent.indexOf("MSIE")>0)
{
 if(navigator.userAgent.indexOf("MSIE 6.0")>0){alert("您使用的IE6版本过低，建议使用360、Maxthon、Baidu、Chrome、IE 8.0 以上浏览器！");closewin();}
 if(navigator.userAgent.indexOf("MSIE 7.0")>0){alert("您使用的IE7版本过低，建议使用360、Maxthon、Baidu、Chrome、IE 8.0 以上浏览器！");closewin();}
}
function switchSkin(skin)
{
 var style = document.getElementById(skin);
 var tmp = document.getElementsByTagName("style");
 var skinArr = [];
 for(var i = 0; i < tmp.length; i++)
 {
	if(tmp[i].getAttribute("id"))
	{
	 skinArr[i] =  tmp[i].getAttribute("id");
	 document.getElementById(skinArr[i]).disabled = true;
	}
 }
 style.disabled = false;
}
switchSkin("black");
function SDMenu(id)
{
 if (!document.getElementById || !document.getElementsByTagName)
 return false;
 this.menu = document.getElementById(id);
 this.submenus = this.menu.getElementsByTagName("div");
 this.remember = true;
 this.speed = 2;
 this.markCurrent = true;
 this.oneSmOnly = true;
}
SDMenu.prototype.init = function()
{
 var mainInstance = this;
 for (var i = 0; i < this.submenus.length; i++)
	this.submenus[i].getElementsByTagName("span")[0].onclick = function()
	{
	 mainInstance.toggleMenu(this.parentNode);
	};
 if (this.markCurrent)
 {
	var links = this.menu.getElementsByTagName("a");
	for (var i = 0; i < links.length; i++)
	{
	 links[0].className="current";
	 links[i].onclick = function()
	 {
		var link_t = document.getElementsByTagName("a");
		for (var i = 0; i < link_t.length; i++)
		{
		 if(link_t[i].className== "current")
		 {
			link_t[i].className='"'';"'
		 }
		}
		this.className = "current";
	 }
	}
 }
 if (this.remember)
 {
	var regex = new RegExp("sdmenu_" + encodeURIComponent(this.menu.id) + "=([01]+)");
	var match = regex.exec(document.cookie);
	if (match)
	{
	 var states = match[1].split("");
	 for (var i = 0; i < states.length; i++)
		this.submenus[i].className = (states[i] == 0 ? "collapsed" : "");
	}
 }
};
SDMenu.prototype.toggleMenu = function(submenu)
{
 if (submenu.className == "collapsed")
	this.expandMenu(submenu);
 else
	this.collapseMenu(submenu);
};
SDMenu.prototype.expandMenu = function(submenu)
{
 var fullHeight = submenu.getElementsByTagName("span")[0].offsetHeight;
 var links = submenu.getElementsByTagName("a");
 for (var i = 0; i < links.length; i++)
	fullHeight += links[i].offsetHeight;
 var moveBy = Math.round(this.speed * links.length);
 var mainInstance = this;
 var intId = setInterval(function()
 {
	var curHeight = submenu.offsetHeight;
	var newHeight = curHeight + moveBy;
	if (newHeight < fullHeight)
	 submenu.style.height = newHeight + "px";
	else
	{
	 clearInterval(intId);
	 submenu.style.height = "";
	 submenu.className = "";
	 mainInstance.memorize();
	}
 }, 30);
 this.collapseOthers(submenu);
};
SDMenu.prototype.collapseMenu = function(submenu)
{
 var minHeight = submenu.getElementsByTagName("span")[0].offsetHeight;
 var moveBy = Math.round(this.speed * submenu.getElementsByTagName("a").length);
 var mainInstance = this;
 var intId = setInterval(function()
 {
	var curHeight = submenu.offsetHeight;
	var newHeight = curHeight - moveBy;
	if (newHeight > minHeight)
	 submenu.style.height = newHeight + "px";
	else
	{
	 clearInterval(intId);
	 submenu.style.height = "";
	 submenu.className = "collapsed";
	 mainInstance.memorize();
	}
 }, 30);
};
SDMenu.prototype.collapseOthers = function(submenu)
{
 if (this.oneSmOnly)
 {
	for (var i = 0; i < this.submenus.length; i++)
	 if (this.submenus[i] != submenu && this.submenus[i].className != "collapsed")
		this.collapseMenu(this.submenus[i]);
 }
};
SDMenu.prototype.expandAll = function()
{
 var oldOneSmOnly = this.oneSmOnly;
 this.oneSmOnly = true;
 for (var i = 0; i < this.submenus.length; i++)
	if (this.submenus[i].className == "collapsed")
	 this.expandMenu(this.submenus[i]);
	this.oneSmOnly = oldOneSmOnly;
};
SDMenu.prototype.collapseAll = function()
{
 for (var i = 0; i < this.submenus.length; i++)
	if (this.submenus[i].className != "collapsed")
	 this.collapseMenu(this.submenus[i]);
};
SDMenu.prototype.memorize = function()
{
 if (this.remember)
 {
	var states = new Array();
	for (var i = 0; i < this.submenus.length; i++)
	 states.push(this.submenus[i].className == "collapsed" ? 0 : 1);
	var d = new Date();
	d.setTime(d.getTime() + (30 * 24 * 60 * 60 * 1000));
	document.cookie = "sdmenu_" + encodeURIComponent(this.menu.id) + "=" + states.join("") + "; expires=" + d.toGMTString() + "; path=/";
 }
};
var myMenu;
window.onload = function()
{
 myMenu = new SDMenu("my_menu");
 myMenu.init();
 var firstSubmenu = myMenu.submenus[0];
 myMenu.expandMenu(firstSubmenu);
};
</SCRIPT>'>>$LOG 2>&1

$E '<div class=top><TABLE height=55 cellSpacing=0 cellPadding=0 width=100% border=0 style="min-width:970px;"><TBODY><TR>
<TD><a href="http://www.TianYi.com" target="_blank"><IMG border=0 alt="如果IE版本过旧,则无法显示此图片!" hspace=0 src="data:image/png;base64,
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"></a>
</TD>'"<TD class=body></TD>"'
<TD align=right><a href="mailto:TianYi@foxmail.com?subject=Sysinfo_LIN_V1.3">
<IMG border=0 alt="如果IE版本过旧,则无法显示此图片!" hspace=0 src="data:image/png;base64,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
X7iIAAAAASUVORK5CYII="></a></TD></TR></TBODY></TABLE></div>'>>$LOG 2>&1

#Function
HR(){ if [[ Draw_hr -eq 0 ]];then Draw_hr=1;else EE "<br><hr class=hr1><br></hr>";fi;}
HREF(){ ((href=href+1));EE "<a name=$href></a>";}
P_CMD()
{
 EE "<table class=cmdtab cellspacing=2px cellpadding=0><tr><td CLASS=tabtop>"
 case $2 in
	"N") EE "$1</td></tr></table>";;
	"$") EE "$ $1</td></tr></table>";;
	"SQL") $E "SQL> $1</td></tr></table>">>$LOG 2>&1;;
	"ASM") EE "ASMCMD> $1</td></tr></table>";;
	*) EE "# $1</td></tr></table>";;
 esac
}
P_TOP(){ EE "<table class=result cellSpacing=10 cellPadding=0 align=left><tr><td class=td2><pre>";}
P_BOT(){ EE "</pre></td></tr></table><hr class=bothr></hr>";}
P(){ if [[ -z "$2" ]];then EE "No rows output.";else cmd "$1";fi;}
M_BEGIN(){ href=$1;EE "<div><span><a href=#$1><b>$2</b></a></span>";}
M_END(){ EE "</div>";}
M_SUB(){ ((href=href+1));EE "<a href=#$href><li>$1$2</li></a>";}

EE "<div class=left><div align=left><div id=my_menu class=sdmenu><div><span><a href=#Top0000><b>基本信息</b></a></span></div>"
if [[ $CHK_OS = "Y" ]];then
 M_BEGIN 1 "系统信息"
 for col in "uname -a" "lsb_release -a" "lilo boot manager" "grub boot manager" "palo boot manager" "lsmod" "kernel commandline" "getconf -a" "sysctl -a" "cat /etc/sysctl.conf" "ls -l /boot" "last|grep boot" "cpuinfo" "meminfo" "pagetypeinfo" "zoneinfo" "used memory and swap" "LANG setting" "ulimit -a" "inittab" "groups" "users" "chkconfig --list" "ipcs -u" "ipcs -l" "crontab -l" "at -l" "dmidecode" "list of devices" "PCI devices" "SCSI devices" "SMART disk drive information" "packages installed" "xorg.conf";do
	case $col in
	 "lsb_release -a") [[ -x /usr/bin/lsb_release ]] && M_SUB "$col";;
	 "lilo boot manager") [[ -f /etc/lilo.conf ]] && M_SUB "$col";;
	 "grub boot manager") [[ -f /boot/grub/menu.lst ]] && M_SUB "$col";;
	 "palo boot manager") [[ -f /etc/palo.conf ]] && M_SUB "$col";;
	 "pagetypeinfo") [[ -r /proc/pagetypeinfo ]] && M_SUB "$col";;
	 "inittab") [[ -r /etc/inittab ]] && M_SUB "$col";;
	 "chkconfig --list")
		which chkconfig >/dev/null 2>&1
		[[ $? -eq 0 ]] && M_SUB "$col";;
	 "list of devices")
		which lshal >/dev/null 2>&1
		[[ $? -eq 0 ]] && M_SUB "$col";;
	 "dmidecode")
		DMIDECODE=$(which dmidecode 2>/dev/null)
		if [[ -n "$DMIDECODE" ]] && [[ -x $DMIDECODE ]];then DMIDECODE="Y";M_SUB "$col";fi;;
	 "SMART disk drive information")
		SMARTCTL=$(which smartctl 2>/dev/null)
		if [[ -n "$SMARTCTL" ]] && [[ -x $SMARTCTL ]];then M_SUB "$col";fi;;
	 "xorg.conf") [[ -e /etc/X11/xorg.conf ]] && M_SUB "$col";;
	 *) M_SUB "$col";;
	esac
 done
 M_END
fi
if [[ $CHK_LVM = "Y" ]];then
 M_BEGIN 51 "LVM 信息"
 for col in "blkid" "fdisk -l" "partition layout" "partitions to restore from" "lvm version" "pvdisplay" "volume groups" "logical volumes" "cat /etc/fstab" "df -ah" "filesystems parameters";do
	case $col in
	 "blkid") [[ -x /sbin/blkid ]] && M_SUB "$col";;
	 "partition layout") [[ -x /sbin/parted ]] && M_SUB "$col";;
	 "partitions to restore from") [[ -x /sbin/sfdisk ]] && M_SUB "$col";;
	 "lvm version") pvdisplay 2>/dev/null >$LOG.pv;if [[ -n `cat $LOG.pv|grep -v "open failed"` ]];then PV="Y";M_SUB "$col";fi;;
	 "pvdisplay"|"volume groups"|"logical volumes") [[ "$PV" = "Y" ]] && M_SUB "$col";;
	 "filesystems parameters") [[ -x /sbin/dumpe2fs ]] && M_SUB "$col";;
	 *) M_SUB "$col";;
	esac
 done
 M_END
fi
if [[ $CHK_NET = "Y" ]];then
 NETSTAT_VER=`netstat -V | awk '/netstat/ { if ( $2 < 1.38 ) { print "NO" } else { print "OK" }}'`
 M_BEGIN 101 "网络信息"
 for col in "ifconfig" "ip addr" "NIC statistics" "LAN configuration files" "network neighborhood" "ip route" "netstat -r" "netstat -s" "netstat -ai" "all sockets" "tcp listening sockets" "udp listening sockets" "services" "dns/named" "resolv.conf" "/etc/hosts" "hosts.allow" "hosts.deny" "ntp.conf" "sshd config" "ssh config" "syslog.conf" "/etc/xinetd.d";do
	case $col in
	 "netstat -r"|"netstat -s"|"netstat -ai"|"all sockets") [[ "$NETSTAT_VER" = "OK" ]] && M_SUB "$col";;
	 "tcp listening sockets"|"udp listening sockets") [[ -x /usr/sbin/ss ]] && M_SUB "$col";;
	 "dns/named") [[ -r /etc/bind/named.boot ]] && M_SUB "$col";;
	 "resolv.conf") [[ -f /etc/resolv.conf ]] && M_SUB "$col";;
	 "hosts.allow") [[ -f /etc/hosts.allow ]] && M_SUB "$col";;
	 "hosts.deny") [[ -f /etc/hosts.deny ]] && M_SUB "$col";;
	 "ntp.conf") [[ -f /etc/ntp.conf ]] && M_SUB "$col";;
	 "sshd config") [[ -f /etc/ssh/sshd_config ]] && M_SUB "$col";;
	 "ssh config") [[ -f /etc/ssh/ssh_config ]] && M_SUB "$col";;
	 "syslog.conf") [[ -f /etc/syslog.conf ]] && M_SUB "$col";;
	 "/etc/xinetd.d") [[  -d /etc/xinetd.d ]] && M_SUB "$col";;
	 *) M_SUB "$col";;
	esac
 done
 M_END
fi
if [[ $CHK_PER = "Y" ]];then
 M_BEGIN 151 "性能信息"
 for col in "top cpu" "top memory" "top file handles" "top" "vmstat" "mpstat" "sar" "iostat" "ipcs";do
	which `$E $col|awk '{print $1}'`>/dev/null 2>&1
	if [[ $? -eq 0 ]];then M_SUB "$col";fi
 done
 M_END
fi
if [[ $CHK_STO = "Y" ]];then
 M_BEGIN 201 "存储信息"
 for col in "multipath version" "multipath devices information" "multipath configuration file" "device mapper files" "multipath bindings" "emcpreg -list" "powermt version" "powermt display paths" "powermt display dev=all" "dlnkmgr view -sys" "dlnkmgr view -path" "dlnkmgr view -drv" "dlnkmgr view -path -item lu hd";do
	case $col in
	 "multipath version"|"multipath devices information")
		if [[ -x /sbin/multipath ]];then
		 if [[ "$col" = "multipath version" ]];then
			M_SUB "$col"
		 else
			multipath -v2 -d -ll >${LOG}.log 2>&1
			if { [[ -n `cat ${LOG}.log` ]] && [[ -z `cat ${LOG}.log|grep "does not exist"` ]] && [[ -z `cat ${LOG}.log|grep "driver not loaded"` ]]; } then MULTIPATH="Y";M_SUB "$col";fi
			RM "${LOG}.log"
		 fi
		fi;;
	 "multipath configuration file"|"device mapper files"|"multipath bindings") [[ -n $MULTIPATH ]] && M_SUB "$col";;
	 "dlnkmgr view -sys"|"dlnkmgr view -path"|"dlnkmgr view -drv"|"dlnkmgr view -path -item lu hd") if [[ -n `rpm -qa HDLM` ]] && [[ -x /opt/DynamicLinkManager/bin/dlnkmgr ]];then M_SUB "$col";fi;;
	 *)
		which `$E $col|awk '{print $1}'`>/dev/null 2>&1
		if [[ $? -eq 0 ]];then M_SUB "$col";fi;;
	esac
 done
 M_END
fi
if { [[ $CHK_HA = "Y" ]] && [[ -x /usr/sbin/cman_tool ]]; } then
 M_BEGIN 251 "RHCS 信息"
 for col in "cluster status" "cluster nodes" "cluster services" "cluster configuration" "rgmanager.log";do
	case $col in
	 "cluster status"|"cluster nodes"|"cluster services") M_SUB "$col";;
	 "cluster configuration") [[ -r /etc/cluster/cluster.conf ]] && M_SUB "$col";;
	 *) [[ -r /var/log/cluster/rgmanager.log ]] && M_SUB "$col";;
	esac
 done
 M_END
fi
if [[ $CHK_LOG = "Y" ]];then
 M_BEGIN 301 "日志信息"
 for col in "last" "messages" "lastlog" "btmp" "boot.log" "secure" "maillog" "cron" "spooler";do
	if [[ "$col" = "last" ]];then
	 which $col >/dev/null 2>&1
	 [[ $? -eq 0 ]] && M_SUB "$col"
	else [[ -f "/var/log/$col" ]] && M_SUB "$col";fi
 done
 M_END
fi
if [[ $CHK_ORA = "Y" ]];then
 if [[ -n `grep -w oracle /etc/passwd` ]];then
	su - oracle -c "which sqlplus">/dev/null 2>&1
	if [[ $? -ne 0 ]];then CHK_ORA="N"
	else
	 crs_user=oracle
	 CHK_CRS="N"
	 if [[ `ps -ef|grep crs|grep -v grep|wc -l` -gt 0 || `ps -ef|grep has|grep -v grep|wc -l` -gt 0 && `ps -ef|grep d.bin|grep -v grep|wc -l` -gt 0 ]];then
		if [[ `ps -ef|grep grid|egrep -v grep|wc -l` -gt 1 ]];then crs_user=grid;fi
		su - $crs_user -c "which crsctl crs_stat srvctl ocrcheck ocrconfig">/dev/null 2>&1
		if [[ $? -eq 0 ]];then CHK_CRS="Y";fi
	 fi
	 CHK_ASM="N"
	 su - $crs_user -c "which asmcmd sqlplus">/dev/null 2>&1
	 if [[ $? -eq 0 ]];then
		asm_instance_name=`ps -ef|grep smon|egrep -v grep|awk '{print $NF}'|awk 'sub("asm_smon_","",$NF) {print $NF}'|sed -e 's/(//g' -e 's/)//g'`
		if [[ -n "$asm_instance_name" ]];then CHK_ASM="Y";fi
	 fi
	 CHK_OPATCH="N"
	 if [[ $crs_user = "grid" ]];then
		su - grid -c "env|grep ORACLE_HOME">ora_home.$$ 2>&1
		GRID_HOME=`cat ora_home.$$|grep ORACLE_HOME|awk 'BEGIN {FS="="}{print $2}'`
	 fi
	 su - oracle -c "env|grep ORACLE_HOME">ora_home.$$ 2>&1
	 ORA_HOME=`cat ora_home.$$|grep ORACLE_HOME|awk 'BEGIN {FS="="}{print $2}'`
	 RM "ora_home.$$"
	 if [[ -n "$ORA_HOME" ]];then
		su - oracle -c "$ORA_HOME/OPatch/opatch lsinventory -all">${LOG}.log 2>&1 &
		sleep 10
		cat ${LOG}.log|grep -q "succeeded"
		[[ $? -eq 0 ]] && CHK_OPATCH="Y"
		RM "${LOG}.log"
	 fi
	fi
 else CHK_ORA="N";fi
fi
if [[ $CHK_ORA = "Y" ]];then
 M_BEGIN 351 "ORACLE 信息"
 if [[ $CHK_CRS = "Y" ]];then
	if [[ `ps -ef|grep crs|grep -v grep|wc -l` -gt 0 ]];then M_SUB "crsctl check crs";else M_SUB "crsctl check has";fi
	for col in "crsctl status resource" "srvctl status listener" "srvctl status database" "votedisk check" "ocrcheck" "display ocrconfig backup";do
	 if [[ $col = "srvctl status listener" ]];then
		if [[ $crs_user = "grid" ]];then M_SUB "$col";fi
	 else M_SUB "$col";fi
	done
	IsDrawLine="Y"
 fi
 if [[ $CHK_ASM = "Y" ]];then
	for col in "srvctl status asm" "asmcmd lsdg" "asm instance information" "asm disk information" "asm diskgroup information" "asm spfile parameter";do
	 M_SUB "$col"
	done
	IsDrawLine="Y"
 fi
 if [[ "$IsDrawLine" = "Y" ]];then EE "<br>";fi

 db_count=0
 instance_name=`ps -ef|grep smon|egrep -v grep|awk '{print $NF}'|awk 'sub("ora_smon_","",$NF) {print $NF}'|sed -e 's/(//g' -e 's/)//g'`
 for db_name in $instance_name;do
	((db_count=db_count+1))
	if [[ $db_count -gt 1 ]];then EE "<br>";fi
	if [[ $db_count -lt 2 ]];then
	 for col in "database version" "installed products";do
		M_SUB "$col"
	 done
	 if [[ $CHK_OPATCH = "Y" ]];then
		if { [[ `ps -ef|grep grid|egrep -v grep|wc -l` -gt 1 ]] && [[ -n "$GRID_HOME" ]]; } then
		 M_SUB "opatch information [grid]"
		 M_SUB "opatch information [oracle]"
		else M_SUB "opatch information";fi
	 fi
	 EE "<br>"
	fi
	for col in "instance information" "character set" "system global area" "pga and advice" "spfile location" "show parameter" "archive mode" "database controlfiles" "database redolog files" "redolog switching frequency" "archivelog infomation" "tablespace summary" "temporary tablespaces" "datafile status" "datafile size" "datafiles total size" "segments total size" "resource limit" "is configured dataguard and force_logging" "users information" "hit rate of the shared pool size" "hit rate of the data buffer" "hit rate of the data dictionary" "hit rate of the sorts" "redo log buffer retry ratio" "lock contention rate" "is configuared flashback" "database links" "data scheduler jobs" "database jobs" "number of sessions" "session wait several" "top cpu users" "invalid objects" "dba role users info" "system parameter file" "rman automatically backup configuration" "Rman Backup Job last 10" "lock object info" "wait events last 1 day" "last spfile copies" "last controlfile copies" "create users script" "create tablespace script" "alert_${db_name}.log";do
	 if [[ $col = "alert_${db_name}.log" ]];then M_SUB "$col" " [top 1000]";else M_SUB "$col" " [$db_name]";fi
	done
 done
 if [[ $db_count -gt 0 ]];then EE "<br>";fi
 for col in "listener configuration" "Listener Log [top 1000]" "tnsnames configuration" "oracle .profile configuration";do
	M_SUB "$col"
 done
 if [[ `grep grid /etc/passwd` ]];then M_SUB "grid .profile configuration";fi
 M_END
fi
if { [[ $CHK_SF = "Y" ]] && [[ `rpm -qa|grep VRTS|grep -v grep|grep -v VRTSpbx|wc -l` -gt 5 ]]; } then
 M_BEGIN 801 "SF 信息"
 for col in "vxlicrep" "vxdisk -e -o alldgs list" "vxdg list" "vxdg free" "vxprint -vhtIP" "vxprint -htq" "vxprint -st" "vxstat -o alldgs -i 2 -c 8" "vxdmpadm listctlr all" "vxdmpadm listenclosure all" "vxdisk path" "vxdmpadm getsubpaths" "vxgetdmpnames" "vxdctl -c mode" "gabconfig -a" "hastatus -summary" "hares -state" "lltstat" "lltstat -n" "cat /etc/llttab" "cat /etc/VRTSvcs/conf/config/main.cf" "tail -200 /var/VRTSvcs/log/engine_A.log" "vxtask list" "vxsnap -g dg* -vx list";do
	which `$E $col|awk '{print $1}'`>/dev/null 2>&1
	if [[ $? -eq 0 ]];then
	 case $col in
	 "vxdctl -c mode"|"gabconfig -a"|"hastatus -summary"|"hares -state"|"main.cf content"|"engine_A.log [last 200 lines]"|"lltstat"|"lltstat -n"|"llttab content")
		if [[ `rpm -q VRTSllt|wc -l` -gt 0 && `rpm -q VRTSvcs|wc -l` -gt 0 ]];then M_SUB "$col";fi;;
	 "vxstat -o alldgs -i 2 -c 8") if [[ `vxdg list|wc -l` -gt 1 ]];then M_SUB "$col";fi;;
	 *) M_SUB "$col";;
	 esac
	fi
 done
 which vxprint vxtune vxrlink vxrvg vradmin>/dev/null 2>&1
 if [[ $? -eq 0 ]];then
	if [[ -n `vxprint -qV|grep "Disk group"|awk '{print $3}'` ]];then
	 M_SUB "vxtune"
	 for dg in `vxprint -qV|grep "Disk group"|awk '{print $3}'`;do
		M_SUB "$dg volume replicator information"
	 done
	fi
 fi
 M_END
fi
if { [[ $CHK_NBU = "Y" ]] && [[ -e "/usr/openv/netbackup" ]]; } then
 M_BEGIN 901 "NBU 信息"
 for col in "version" "cat bp.conf" "bpgetconfig" "bpminlicense -verbose" "bpps -a" "bpstulist" "tpconfig -d" "tpclean" "available_media" "bpcatlist -since-days 15";do
	case $col in
	"bpgetconfig"|"bpminlicense -verbose"|"bpstulist"|"bpcatlist -since-days 15") if [[ -e /usr/openv/netbackup/bin/admincmd ]];then M_SUB "$col";fi;;
	"tpconfig -d"|"tpclean") if [[ -e /usr/openv/volmgr/bin ]];then M_SUB "$col";fi;;
	"available_media") if [[ -e /usr/openv/netbackup/bin/goodies/available_media ]];then M_SUB "$col";fi;;
	*) M_SUB "$col";;
	esac
 done
 M_END
fi
EE "</div></div></div>"
$E '<div class=main><div id="colordiv"><table border=0 cellspacing=0 cellpadding=0><tr><td>风格切换|</td>
<td width=21px align=right><table class=tabblack onclick=switchSkin("black");></table></td>
<td width=23px align=right><table class=tabwhite onclick=switchSkin("white");><tr></tr></table></td></tr>
</table></div><a name=Top0000></a><table class=tab1><tr><td valign=top><pre><table><tr height=25>
<td class=td1 width=120px>1、推荐的分辨率</td><td class=td1>1024 * 768 以上</td></tr><tr height=25>
<td class=td1>2、推荐的浏览器</td><td class=td1>360、Baidu、Chrome、IE 8.0 以上浏览器</td></tr><tr height=25>
<td class=td1>3、支持操作系统</td><td class=td1>RedHat、Oracle Linux、CentOS、UBuntu 及 SUSE</td></tr><tr height=25>
<td class=td1>4、收集信息内容</td><td class=td1>系统、LVM、存储、性能、网络、RHCS、日志、ORACLE、STORAGE FOUNDATION、NETBACKUP</td></tr></table>
<table class=coltable width=745px border=0 cellspacing=1 cellpadding=1 align=left><tr class=bg0>
<th class=tableheader width=34%>脚本更新时间</th><td width=66% class=td3>'"${UpdateTime}</td></tr><tr class=bg1>
<th class=tableheader>信息收集时间</th><td class=td3>${Date}</td></tr><tr class=bg0>
<th class=tableheader>机器型号</th><td class=td3>${Type}</td></tr><tr class=bg1>
<th class=tableheader>机器SN号</th><td class=td3>${SerialNum}</td></tr><tr class=bg0>
<th class=tableheader>系统版本</th><td class=td3>${OSVersion}</td></tr><tr class=bg1>
<th class=tableheader>内核版本</th><td class=td3>${KernelVersion}</td></tr><tr class=bg0>
<th class=tableheader>主机名</th><td class=td3>${HostName}</td></tr><tr class=bg1>
<th class=tableheader>IP地址</th><td class=td3>${IP_Addr}</td></tr><tr class=bg0>
<th class=tableheader>当前RunLevel</th><td class=td3>${CurRunLevel}</td></tr><tr class=bg1>
<th class=tableheader>默认RunLevel</th><td class=td3>${DefRunLevel}</td></tr><tr class=bg0>
<th class=tableheader>系统安装时间</th><td class=td3>${InstallTime}</td></tr><tr class=bg1>
<th class=tableheader>系统运行时间</th><td class=td3>${UPTime}</td></tr><tr class=bg0>
<th class=tableheader>收集信息的机器IP</th><td class=td3>${Logon_IP}</td></tr></table></pre></td></tr></table><br>">>$LOG 2>&1
#系统信息
if [[ $CHK_OS = "Y" ]];then
 $E "Get system information....";HR;href=0;HREF
 for command in "uname -a" "lsb_release -a" "lilo boot manager" "grub boot manager" "palo boot manager" "lsmod" "kernel commandline" "getconf -a" "sysctl -a" "cat /etc/sysctl.conf" "ls -l /boot" "last|grep boot" "cpuinfo" "meminfo" "pagetypeinfo" "zoneinfo" "used memory and swap" "LANG setting" "ulimit -a" "inittab" "cat /etc/group" "cat /etc/passwd" "chkconfig --list" "ipcs -u" "ipcs -l" "crontab -l" "at -l" "dmidecode" "list of devices" "PCI devices" "SCSI devices" "SMART disk drive information" "packages installed" "xorg.conf";do
	case $command in
	 "lsb_release -a")
		if [[ -x /usr/bin/lsb_release ]];then HREF;P_CMD "$command";P_TOP;cmd "lsb_release -a";P_BOT;fi;;
	 "lilo boot manager")
		if [[ -f /etc/lilo.conf ]];then
		 HREF;P_CMD "$command" "N";P_TOP
		 EE "#<b> cat /etc/lilo.conf</b>";grep -vE '^#|^ *$' /etc/lilo.conf >>$LOG 2>&1
		 EE "<b> currently mapped files</b>";cmd "lilo -q"
		 P_BOT;fi;;
	 "grub boot manager")
		if [[ -f /boot/grub/menu.lst ]];then
		 HREF;P_CMD "cat /boot/grub/menu.lst";P_TOP
		 grep -vE '^#|^ *$' /boot/grub/menu.lst >>$LOG 2>&1
		 P_BOT;fi;;
	 "palo boot manager")
		if [[ -f /etc/palo.conf ]];then
		 HREF;P_CMD "cat /etc/palo.conf";P_TOP
		 grep -vE '^#|^ *$' /etc/palo.conf >>$LOG 2>&1
		 P_BOT;fi;;
	 "pagetypeinfo")
		if [[ -r /proc/pagetypeinfo ]];then HREF;P_CMD "cat /proc/pagetypeinfo";P_TOP;cmd "cat /proc/pagetypeinfo";P_BOT;fi;;
	 "inittab") if [[ -r /etc/inittab ]];then HREF;P_CMD "cat /etc/inittab";P_TOP;grep -vE '^#|^ *$' /etc/inittab >>$LOG 2>&1;P_BOT;fi;;
	 "chkconfig --list")
		which chkconfig >/dev/null 2>&1
		if [[ $? -eq 0 ]];then HREF;P_CMD "$command";P_TOP;$command|column -t >>$LOG 2>&1;P_BOT;fi;;
	 "list of devices")
		which lshal >/dev/null 2>&1
		if [[ $? -eq 0 ]];then HREF;P_CMD "lshal";P_TOP;cmd "lshal";P_BOT;fi;;
	 "dmidecode")
		if [[ "$DMIDECODE" = "Y" ]];then HREF;P_CMD "$command";P_TOP;cmd "$command";P_BOT;fi;;
	 "SMART disk drive information")
		SMARTCTL=$(which smartctl 2>/dev/null)
		if [[ -n "$SMARTCTL" ]] && [[ -x $SMARTCTL ]];then
		 HREF;P_CMD "$command" "N";P_TOP;EE "<b>Version:</b>"
		 $SMARTCTL --scan|grep -v "OPTION" |grep -v "summary" >>$LOG 2>&1
		 EE "<b>Details:</b>"
		 PHYS_DRIVES=`fdisk -l 2>&1|sort -u|grep "^Disk "|grep -vE "md[0-9]|identifier:|doesn't contain a valid"|sed -e "s/:.*$//"|awk '{print $2}'`
		 for drive in ${PHYS_DRIVES};do
			EE "<b>-- Drive=$drive --</b>"
			$SMARTCTL -a $drive|grep -v "Copyright"|grep -v "smartmontools" >>$LOG 2>&1
			EE
		 done
		 P_BOT;fi;;
	 "xorg.conf")
		if [[ -e /etc/X11/xorg.conf ]];then
		 HREF;P_CMD "cat /etc/X11/xorg.conf";P_TOP
		 grep -vE '^#|^ *$' /etc/X11/xorg.conf >>$LOG 2>&1
		 P_BOT;fi;;
	 *)
		HREF
		case $command in
		 "lsmod") P_CMD "$command";P_TOP;$command|column -t >>$LOG 2>&1;;
		 "kernel commandline") P_CMD "cat /proc/cmdline";P_TOP;cmd "cat /proc/cmdline";;
		 "cat /etc/sysctl.conf") P_CMD "$command";P_TOP
		 if [[ -n `cat /etc/sysctl.conf|sort -u|grep -v -e ^# -e ^$` ]];then cat /etc/sysctl.conf|sort -u|grep -v -e ^# -e ^$ >>$LOG 2>&1;else P;fi;;
		 "ls -l /boot")
			P_CMD "$command";P_TOP
			if [[ "$UBUNTU" = "Y" ]];then cmd "$command";else $command|column -t >>$LOG 2>&1;fi;;
		 "last|grep boot") P_CMD "$command";P_TOP;last|grep boot >>$LOG 2>&1;;
		 "cpuinfo")
			if [[ -x /usr/bin/lscpu ]];then P_CMD "$command" "N";else P_CMD "cat /proc/cpuinfo";fi
			P_TOP;[[ -x /usr/bin/lscpu ]] && EE "#<b> cat /proc/cpuinfo</b>";cmd "cat /proc/cpuinfo"
			if [[ -x /usr/bin/lscpu ]];then EE;EE "#<b> lscpu</b>";cmd "/usr/bin/lscpu";fi;;
		 "meminfo")
			if [[ "$DMIDECODE" = "Y" ]];then
			 P_CMD "Memory Information" "N";P_TOP;EE "<b>Size and Speed</b>"
			 dmidecode|grep -P -A13 "Memory\s+Device" |grep "^.[S]..e"|column -t > ${LOG}.log 2>&1
			 row=1;tmp_id=0;rows=1
			 EE "<table class=coltable width=500px border=0 cellspacing=1 cellpadding=1 align=left><tr><th class=tableheader width=50%>SIZE</th><th class=tableheader>SPEED</th></tr>"
			 while IFS= read -r line;do
				if [[ $row -eq 1 ]];then
				 if [[ -z `$E $line|grep "Installed"` ]];then
					EE "<tr class=bg$tmp_id>"'<td class=td3>'"`$E $line|awk '{print $2" "$3" "$4" "$5" "$6}'`</td>";((rows=rows+1))
					if [[ $tmp_id -eq 0 ]];then tmp_id=1;else tmp_id=0;fi
				 else row=-1;fi
				fi
				if [[ $row -eq 2 ]];then EE '<td class=td3>'"`$E $line|awk '{print $2" "$3" "$4" "$5" "$6}'`</td></tr>";row=0;fi
				((row=row+1))
			 done < ${LOG}.log
			 EE "</table>"
			 ((rows=rows*2))
			 while [[ rows -gt 0 ]];do EE;((rows=rows-1));done
			 EE "#<b> cat /proc/meminfo</b>"
			else P_CMD "cat /proc/meminfo";P_TOP;fi
			cat /proc/meminfo|column -t >>$LOG 2>&1;RM "${LOG}.log";;
		 "zoneinfo") P_CMD "cat /proc/zoneinfo";P_TOP;cmd "cat /proc/zoneinfo";;
		 "used memory and swap") P_CMD "free -toml;$E;free -tm;$E;swapon -s";P_TOP;cmd "free -toml";EE;cmd "free -tm";EE;cmd "swapon -s";;
		 "LANG setting")
			P_CMD "$command" "N";P_TOP;EE "LANG setting: $LANG"
			[[ -r /etc/sysconfig/i18n ]] && cmd "cat /etc/sysconfig/i18n"
			[[ -x /usr/bin/locale ]] && export LANG="C";export LANG_ALL="C";;
		 "at -l") P_CMD "$command";P_TOP;cmd "$command" "Y";;
		 "PCI devices") P_CMD "lspci -v";P_TOP;cmd "lspci -v";;
		 "SCSI devices") P_CMD "cat /proc/scsi/scsi";P_TOP;cmd "cat /proc/scsi/scsi";;
		 "packages installed")
			if [[ "$UBUNTU" = "Y" ]];then P_CMD "dpkg -l";P_TOP;cmd "dpkg -l"
			else
			 P_CMD "$command" "N";P_TOP
			 EE "NAME&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;VERSION&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;RELEASE&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;SIZE&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;INSTALLTIME"
			 PP "-" "112"
			 rpm -qa --queryformat '%{NAME} %{VERSION} %{RELEASE} %{SIZE} %{INSTALLTIME:date}\n'|sort -d -f|column -t >>$LOG 2>&1
			fi;;
		 *) P_CMD "$command";P_TOP;cmd "$command";;
		esac
		P_BOT
	 ;;
	esac
 done
fi
#LVM信息
if [[ $CHK_LVM = "Y" ]];then
 $E "Get LVM information....";HR;href=50;HREF
 for command in "blkid" "fdisk -l" "partition layout" "partitions to restore from" "lvm version" "pvdisplay" "volume groups" "logical volumes" "cat /etc/fstab" "df -ah" "filesystems parameters";do
	case $command in
	 "blkid") if [[ -x /sbin/blkid ]];then HREF;P_CMD "$command";P_TOP;$command|column -t >>$LOG 2>&1;P_BOT;fi;;
	 "partition layout")
		if [[ -x /sbin/parted ]];then
		 HREF;P_CMD "$command" "N";P_TOP
		 for i in $(fdisk -l 2>/dev/null|grep "^Disk "|grep "/dev/"|cut -f1 -d:|cut -f2 -d" ");do
			/sbin/parted -s $i print >${LOG}.log 2>&1
			[[ $? -eq 0 ]] && cmd "cat ${LOG}.log"
		 done
		 RM "${LOG}.log"
		 P_BOT;fi;;
	 "partitions to restore from")
		if [[ -x /sbin/sfdisk ]];then
		 HREF;P_CMD "$command" "N";P_TOP;sfdisk -d 2>/dev/null >${LOG}.log;cmd "cat ${LOG}.log"
		 RM "${LOG}.log"
		 EE;EE;EE "<b>To restore your partitions use the output information: read the man page for sfdisk for usage. ( Hint: sfdisk --force /dev/device < file.save )</b>";P_BOT;fi;;
	 "filesystems parameters")
		if [[ -x /sbin/dumpe2fs ]];then
		 HREF;P_CMD "$command";P_TOP
		 for fs in $(grep ext[2-4] /proc/mounts|awk '{print $1}'|sort -u);do cmd "dumpe2fs -h $fs";done
		 [[ -z "$fs" ]] && P
		 P_BOT;fi;;
	 "lvm version"|"pvdisplay"|"volume groups"|"logical volumes")
		if [[ "$PV" = "Y" ]];then
		 HREF
		 case $command in
			"lvm version"|"pvdisplay") P_CMD "$command";P_TOP;if [[ "$command" = "pvdisplay" ]];then cat $LOG.pv|grep -v "open failed">>$LOG;RM "$LOG.pv";else cmd "$command";fi;;
			 "volume groups")
				P_CMD "$command" "N";P_TOP
				vgdisplay -s >${LOG}.log 2>&1
				if [[ -z `cat ${LOG}.log|grep "No volume groups found"` ]];then
				 for vg in `cat ${LOG}.log|grep -v "/dev/"|awk '{print $1}'`;do name=`$E $vg|sed 's/\"//g'`;EE "#<b> vgdisplay -v $name</b>";cmd "vgdisplay -v $name" "Y";done
				fi
				[[ -z $name ]] && P
				RM "${LOG}.log";;
			 "logical volumes")
				P_CMD "lvs -o +devices";P_TOP;lvs -o +devices 2>/dev/null >${LOG}.log
				if [[ -z `cat ${LOG}.log` ]];then P;else cmd "cat ${LOG}.log" "Y";fi
				RM "${LOG}.log";;
		 esac
		 P_BOT
		fi;;
	 *)
		HREF
		case $command in
		 "fdisk -l") P_CMD "$command";P_TOP;/sbin/fdisk -l 2>/dev/null|sed 's/8e \ Unknown/8e \ LVM/g' >>$LOG 2>&1;;
		 "df -ah") P_CMD "$command";P_TOP;$command|column -t >>$LOG 2>&1;;
		 "cat /etc/fstab") P_CMD "cat /etc/fstab";P_TOP;grep -v '^#' /etc/fstab|column -t >>$LOG 2>&1;;
		 *) P_CMD "$command";P_TOP;cmd "$command";;
		esac
		P_BOT;;
	esac
 done
fi
#网络信息
if [[ $CHK_NET = "Y" ]];then
 $E "Get network information....";HR;href=100;HREF
 for command in "ifconfig" "ip addr" "NIC statistics" "LAN configuration files" "network neighborhood" "ip route" "netstat -r" "netstat -s" "netstat -ai" "all sockets" "tcp listening sockets" "udp listening sockets" "cat /etc/services" "dns/named" "resolv.conf" "hosts" "hosts.allow" "hosts.deny" "ntp.conf" "sshd config" "ssh config" "syslog.conf" "/etc/xinetd.d";do
	case $command in
	 "netstat -r"|"netstat -s"|"netstat -ai"|"all sockets")
		if [[ "$NETSTAT_VER" = "OK" ]];then
		 HREF
		 if [[ "$command" = "all sockets" ]];then P_CMD "netstat -anp";else P_CMD "$command";fi
		 P_TOP
		 if [[ "$command" = "all sockets" ]];then cmd "netstat -anp"
		 elif [[ "$command" = "netstat -s" ]];then cmd "$command"
		 else $command|column -t >>$LOG 2>&1
		 fi
		 P_BOT;fi;;
	 "tcp listening sockets"|"udp listening sockets")
		if [[ -x /usr/sbin/ss ]];then
		 HREF
		 if [[ "$command" = "tcp listening sockets" ]];then P_CMD "ss -planeto";else P_CMD "ss -planeuo";fi
		 P_TOP
		 if [[ "$command" = "tcp listening sockets" ]];then ss -planeto|column -t >>$LOG 2>&1;else ss -planeuo|column -t >>$LOG 2>&1;fi
		 P_BOT;fi;;
	 "dns/named") if [[ -r /etc/bind/named.boot ]];then HREF;P_CMD "cat /etc/named.boot";P_TOP;grep -v '^;' /etc/named.boot >>$LOG 2>&1;P_BOT;fi;;
	 "resolv.conf")
		if [[ -f /etc/resolv.conf ]];then
		 HREF
		 if [[ -f /etc/nsswitch.conf ]];then P_CMD "resolv.conf | nsswitch.conf" "N";else P_CMD "resolv.conf" "N";fi
		 P_TOP
		 EE "#<b> cat /etc/resolv.conf</b>"
		 if [[ -n `grep -vE '^#|^ *$' /etc/resolv.conf` ]];then grep -vE '^#|^ *$' /etc/resolv.conf >>$LOG 2>&1;else P;fi
		 EE
		 if [[ -f /etc/nsswitch.conf ]];then
			EE "#<b> cat /etc/nsswitch.conf</b>"
			if [[ -n `grep -vE '^#|^ *$' /etc/nsswitch.conf` ]];then grep -vE '^#|^ *$' /etc/nsswitch.conf >>$LOG 2>&1;else P;fi
		 fi
		 P_BOT;fi;;
	 "hosts.allow")
		if [[ -f /etc/hosts.allow ]];then
		 HREF;P_CMD "cat /etc/hosts.allow";P_TOP
		 if [[ -n `grep -vE '^#|^ *$' /etc/hosts.allow` ]];then grep -vE '^#|^ *$' /etc/hosts.allow >>$LOG 2>&1;else P;fi
		 P_BOT;fi;;
	 "hosts.deny")
		if [[ -f /etc/hosts.deny ]];then
		 HREF;P_CMD "cat /etc/hosts.deny";P_TOP
		 if [[ -n `grep -vE '^#|^ *$' /etc/hosts.deny` ]];then grep -vE '^#|^ *$' /etc/hosts.deny >>$LOG 2>&1;else P;fi
		 P_BOT;fi;;
	 "ntp.conf") if [[ -f /etc/ntp.conf ]];then HREF;P_CMD "cat /etc/ntp.conf";P_TOP;grep -vE '^#|^ *$' /etc/ntp.conf >>$LOG 2>&1;P_BOT;fi;;
	 "sshd config") if [[ -f /etc/ssh/sshd_config ]];then HREF;P_CMD "cat /etc/ssh/sshd_config";P_TOP;grep -vE '^#|^ *$' /etc/ssh/sshd_config >>$LOG 2>&1;P_BOT;fi;;
	 "ssh config") if [[ -f /etc/ssh/ssh_config ]];then HREF;P_CMD "cat /etc/ssh/ssh_config";P_TOP;grep -vE '^#|^ *$' /etc/ssh/ssh_config >>$LOG 2>&1;P_BOT;fi;;
	 "syslog.conf") if [[ -f /etc/syslog.conf ]];then HREF;P_CMD "cat /etc/syslog.conf";P_TOP;grep  -vE '^#|^ *$' /etc/syslog.conf >>$LOG 2>&1;P_BOT;fi;;
	 "/etc/xinetd.d") if [[ -d /etc/xinetd.d ]];then HREF;P_CMD "cat /etc/xinetd.d/*";P_TOP;cat /etc/xinetd.d/*|grep -vE '^#|^ *$' >>$LOG 2>&1;P_BOT;fi;;
	 *)
		HREF
		case $command in
		 "NIC statistics") P_CMD "ip -s l";P_TOP;cmd "ip -s l";;
		 "LAN configuration files")
			if [[ "$UBUNTU" = "Y" ]];then P_CMD "cat /etc/network/interfaces";P_TOP;cmd "cat /etc/network/interfaces" "Y"
			else
			 P_CMD "$command" "N";P_TOP
			 if [[ "$SUSE" = "Y" ]];then
				for CfgFile in /etc/sysconfig/network/ifcfg-*;do EE "<b>$(basename ${CfgFile}):</b>";cmd "cat ${CfgFile}";EE;done
			 else
				for CfgFile in /etc/sysconfig/network-scripts/ifcfg-*;do EE "<b>$(basename ${CfgFile}):</b>";cmd "cat ${CfgFile}";EE;done
			fi fi;;
		 "network neighborhood") P_CMD "ip neigh";P_TOP;ip neigh|column -t >>$LOG 2>&1;;
		 "ip route") P_CMD "$command";P_TOP;ip route|column -t >>$LOG 2>&1;;
		 "hosts") P_CMD "cat /etc/hosts";P_TOP;grep -vE '^#|^ *$' /etc/hosts >>$LOG 2>&1;;
		 *) P_CMD "$command";P_TOP;cmd "$command";;
		esac
		P_BOT;;
	esac
 done
fi
#性能信息
if [[ $CHK_PER = "Y" ]];then
 $E "Get performance information....";HR;href=150;HREF
 for command in "top cpu" "top memory" "top file handles" "top" "vmstat" "mpstat" "sar -A" "iostat" "ipcs";do
	which `$E $command|awk '{print $1}'`>/dev/null 2>&1
	if [[ $? -eq 0 ]];then
	 HREF
	 case $command in
		"top cpu"|"top memory"|"top file handles")
		 P_CMD "$command [30]" "N";P_TOP
		 if [[ "$command" = "top cpu" ]];then ps -ef|cut -c39-|sort -nr|head -30|awk '{printf("%10s %s\n", $1, $2);}' >>$LOG 2>&1
		 elif [[ "$command" = "top memory" ]];then ps -e -o 'vsz pid ruser cpu time args'|sort -nr|head -30 >>$LOG 2>&1
		 else
			EE "Nr.OpenFileHandles  PID  Command+Commandline"
			(ls /proc/|awk '{if($1+0==0) print " ";else system("$E `ls /proc/"$1+0"/fd |wc -l` \t  PID="$1" \t  CMD=`cat /proc/"$1+0"/cmdline` ")}'|sort -nr|head -30) 2> /dev/null >>$LOG 2>&1
		 fi
		 P_BOT;;
		"top")
		 P_CMD "$command -b -d 2 -n 5";P_TOP;stat=0
		 while [[ $stat -lt 5 ]];do ((stat=stat+1));top -b|head -40 >>$LOG 2>&1;PP "-" "80";sleep 2;done
		 P_BOT;;
		"vmstat") P_CMD "$command" "N";P_TOP  ;EE "# <b>vmstat 2 5</b>";cmd "vmstat 2 5";EE;EE "# <b>vmstat -dn</b>";cmd "vmstat -dn";EE;EE "# <b>vmstat -f</b>";cmd "vmstat -f";P_BOT;;
		"mpstat"|"iostat") P_CMD "$command 2 5";P_TOP;cmd "$command 2 5";P_BOT;;
		*) P_CMD "$command";P_TOP;cmd "$command";P_BOT;;
	 esac
	fi
 done
fi
#存储信息
if [[ $CHK_STO = "Y" ]];then
 $E "Get storage information....";HR;href=200;HREF
 for command in "rpm -qa|grep mapper" "multipath -v2 -d -ll" "cat /etc/multipath.conf" "ls -l /dev/mapper" "cat /var/lib/multipath/bindings" "emcpreg -list" "powermt version" "powermt display paths" "powermt display dev=all" "dlnkmgr view -sys" "dlnkmgr view -path" "dlnkmgr view -drv" "dlnkmgr view -path -item lu hd";do
	case $command in
	 "rpm -qa|grep mapper"|"multipath -v2 -d -ll")
		if [[ -x /sbin/multipath ]];then
		 if [[ "$command" = "rpm -qa|grep mapper" ]];then HREF;P_CMD "$command";P_TOP;rpm -qa|grep mapper >>$LOG 2>&1;P_BOT
		 else
			if [[ -n $MULTIPATH ]];then HREF;P_CMD "$command";P_TOP;cmd "multipath -v2 -d -ll";P_BOT;fi
		 fi fi;;
	 "cat /etc/multipath.conf"|"ls -l /dev/mapper"|"cat /var/lib/multipath/bindings")
		if [[ -n $MULTIPATH ]];then
		 HREF
		 if [[ "$command" = "ls -l /dev/mapper" ]];then P_CMD "$command" "N";else P_CMD "$command";fi
		 P_TOP
		 if [[ "$command" = "cat /etc/multipath.conf" ]];then grep -vE '^#|^ *$' /etc/multipath.conf >>$LOG 2>&1
		 elif [[ "$command" = "ls -l /dev/mapper" ]];then for MultiPath in $(/sbin/multipath -v1 -d -l);do cmd "ls -l /dev/mapper/$MultiPath";done
		 else cmd "$command"
		 fi
		 P_BOT;fi;;
	 "dlnkmgr view -sys"|"dlnkmgr view -path"|"dlnkmgr view -drv"|"dlnkmgr view -path -item lu hd") if [[ -n `rpm -qa HDLM` ]] && [[ -x /opt/DynamicLinkManager/bin/dlnkmgr ]];then HREF;P_CMD "$command";P_TOP;cmd "/opt/DynamicLinkManager/bin/$command";P_BOT;fi;;
	 *)
		which `$E $command|awk '{print $1}'`>/dev/null 2>&1
		if [[ $? -eq 0 ]];then HREF;P_CMD "$command";P_TOP;cmd "$command";P_BOT;fi;;
	esac
 done
 if [[ $href -eq 201 ]];then P_CMD "Storage Information";P_TOP;P;P_BOT;fi
fi
#RHCS信息
if { [[ $CHK_HA = "Y" ]] && [[ -x /usr/sbin/cman_tool ]]; } then
 $E "Get RHCS information....";HR;href=250;HREF
 for command in "cluster status" "cluster nodes" "cluster services" "cluster configuration" "rgmanager.log";do
	case $command in
	 "cluster status") HREF;P_CMD "$command" "N";P_TOP;EE "# <b>cman_tool status</b>";cmd "cman_tool status" "Y";EE;EE "# <b>clustat</b>";cmd "clustat" "Y";P_BOT;;
	 "cluster nodes"|"cluster services")
		HREF
		if [[ "$command" = "cluster nodes" ]];then P_CMD "cman_tool nodes";else P_CMD "cman_tool services";fi
		P_TOP
		if [[ "$command" = "cluster nodes" ]];then cmd "cman_tool nodes" "Y";else cmd "cman_tool services" "Y";fi
		P_BOT;;
	 "cluster configuration")
		if [[ -r /etc/cluster/cluster.conf ]];then
		 HREF;P_CMD "cat /etc/cluster/cluster.conf";P_TOP
		 if [[ $(grep -c xml /etc/cluster/cluster.conf) -gt 0 ]];then cat /etc/cluster/cluster.conf|sed 's{<{\&lt{g'|sed 's{>{\&gt{g' >>$LOG 2>&1;else cmd "cat /etc/cluster/cluster.conf" "Y";fi
		 P_BOT;fi;;
	 *) if [[ -r /var/log/cluster/rgmanager.log ]];then HREF;P_CMD "tail -300 /var/log/cluster/rgmanager.log";P_TOP;cmd "tail -300 /var/log/cluster/rgmanager.log" "Y";P_BOT;fi;;
	esac
 done
fi
#日志信息
if [[ $CHK_LOG = "Y" ]];then
 $E "Get LOG information....";HR;href=300;HREF
 for command in "last" "messages" "lastlog" "btmp" "boot.log" "secure" "maillog" "cron" "spooler";do
	if [[ "$command" = "last" ]];then
	 which $command >/dev/null 2>&1
	 if [[ $? -eq 0 ]];then HREF;P_CMD "$command";P_TOP;cmd "$command";P_BOT;fi
	else
	 if [[ -f "/var/log/$command" ]];then
		HREF;P_CMD "tail -500 /var/log/$command";P_TOP
		if [[ "$command" = "lastlog" ]];then cmd "strings /var/log/$command" "Y";else cmd "tail -500 /var/log/$command" "Y";fi
		P_BOT
	 fi
	fi
 done
fi
#ORACLE信息
if [[ $CHK_ORA = "Y" ]];then
 $E "Get database information....";HR;href=350;HREF
 export NLS_LANG='AMERICAN_AMERICA.ZHS16GBK'
 Runcrsctl()
 {
	HREF;P_CMD "$2$3" "$";P_TOP
	if [[ -n "$3" ]];then command="$2$3|awk 'NF'";else command="$2|awk 'NF'";fi
	if [[ -z `su - $1 -c "$command" 2>&1` ]];then P;else su - $1 -c "$command">>$LOG 2>&1;fi
	P_BOT
 }
 RunASMsql()
 {
	HREF
	if [[ $1 = "Y" ]];then
	 P_CMD "$2" "SQL";P_TOP
	 command_output=`su - $crs_user -c "export ORACLE_SID=$asm_instance_name
									 export NLS_LANG='AMERICAN_AMERICA.ZHS16GBK'
									 sqlplus -s /nolog <<EOF
									 connect / as sysdba
									 spool "${LOG}.log"
									 set line 170
									 set long 9999
									 set pagesize 9999
									 $3$4$5$6$7$8
									 spool off
									 quit
									 EOF" 2>&1`
	 $E "$command_output"|grep -q "no rows selected"
	 if [[ $? -eq 0 ]];then EE "No rows selected"
	 else cat ${LOG}.log|egrep -v "rows selected"|egrep -v "PL/SQL procedure successfully completed"|awk 'NF'>>$LOG 2>&1;fi
	 RM "${LOG}.log"
	else
	 if [[ $1 = "$" ]];then P_CMD "$2" "$";else P_CMD "$2" "ASM";fi
	 P_TOP
	 su - $crs_user -c "$3">>$LOG 2>&1
	fi
	P_BOT
 }
 Runsql()
 {
	HREF
	if [[ $1 = "Y" ]];then
	 P_CMD "$2" "SQL";P_TOP
	 command_output=`su - oracle -c "export ORACLE_SID=$db_name
									 export NLS_LANG='AMERICAN_AMERICA.ZHS16GBK'
									 sqlplus -s /nolog <<EOF
									 connect / as sysdba
									 spool "${LOG}.log"
									 set line 170
									 set long 9999
									 set pagesize 9999
									 $3$4$5$6$7$8
									 spool off
									 quit
									 EOF" 2>&1`
	 $E "$command_output"|grep -q "no rows selected"
	 if [[ $? -eq 0 ]];then EE "No rows selected"
	 else cat ${LOG}.log|egrep -v "rows selected"|egrep -v "PL/SQL procedure successfully completed"|awk 'NF'>>${LOG} 2>&1;fi
	 RM "${LOG}.log"
	else
	 P_CMD "$3 $2 $4";P_TOP
	 if [[ $1 = "N_Spfile" ]];then
		su - oracle -c "export ORACLE_SID=$db_name
										sqlplus -s /nolog <<EOF
										connect / as sysdba
										create pfile="\'${LOG}.ora\'" from spfile;
										quit
										EOF">/dev/null 2>&1
		cmd "cat ${LOG}.ora"
		RM "${LOG}.ora"
	 elif [[ $1 = "N_Alert" ]];then
		su - oracle -c "export ORACLE_SID=$db_name
										sqlplus -s /nolog <<EOF
										connect / as sysdba
										spool "${LOG}.log"
										set line 300
										col value_col_plus_show_param for a200
										show parameter background_dump_dest
										spool off
										quit
										EOF">/dev/null 2>&1
		if [[ -e ${LOG}.log ]];then
		 BDUMP=`cat ${LOG}.log|grep -v "VALUE"|grep -v "\-\-\-\-"|awk '{print $3}'|awk 'NF && !/^[[:space:]]/'`
		 RM "${LOG}.log"
		 if [[ -e ${BDUMP}/alert_${db_name}.log ]];then cmd "tail -1000 $BDUMP/alert_${db_name}.log";else P;fi
		fi
	 elif [[ $1 = "N_LSNLog" ]];then
		if [[ -e $LSNLOG ]];then cmd "tail -1000 $LSNLOG";else P;fi
	 else
		if [[ $3 = "cat" ]];then su - $2 -c "cat $4|egrep -v "configuration"|egrep -v "Configuration"">${LOG}.log 2>&1
		else su - $2 -c "$4">${LOG}.log 2>&1;fi
		isnull="N"
		while IFS= read -r line;do
		 $E "$line"|grep -q "No such file"
		 if [[ $? -eq 0 ]];then isnull="";break;fi
		done < ${LOG}.log
		if [[ $isnull = "N" ]];then
		 if [[ $3 = "cat" ]];then cat ${LOG}.log|grep -v "configuration"|grep -v "Configuration">>$LOG 2>&1;else cat ${LOG}.log>>$LOG 2>&1;fi
		else EE "File does not exist.";fi
		RM "${LOG}.log"
	 fi
	fi
	P_BOT
 }

 if [[ $CHK_CRS = "Y" ]];then
	if [[ `ps -ef|grep crs|grep -v grep|wc -l` -gt 0 ]];then Runcrsctl "$crs_user" "crsctl check crs";else Runcrsctl "$crs_user" "crsctl check has";fi
	if [[ $crs_user = "oracle" ]];then Runcrsctl "$crs_user" "crs_stat -t";else Runcrsctl "$crs_user" "crsctl status resource -t";fi
	if [[ $crs_user = "grid" ]];then Runcrsctl "$crs_user" "srvctl status listener";fi
	db_name=`su - $crs_user -c "srvctl config database"`
	db_name1=`$E $db_name|awk 'BEGIN {FS=" "}{print $1}'`
	db_name2=`$E $db_name|awk 'BEGIN {FS=" "}{print $2}'`
	db_name3=`$E $db_name|awk 'BEGIN {FS=" "}{print $3}'`
	db_name4=`$E $db_name|awk 'BEGIN {FS=" "}{print $4}'`
	HREF;P_CMD "srvctl status database $db_name1 $db_name2 $db_name3 $db_name4" "N";P_TOP;isnull="";db_num=0
	for db in "$db_name1" "$db_name2" "$db_name3" "$db_name4";do
	 if [[ -n "$db" ]];then isnull="OK";((db_num=db_num+1));fi
	done
	for db in "$db_name1" "$db_name2" "$db_name3" "$db_name4";do
	 if [[ -n "$db" ]];then
		su - $crs_user -c "srvctl status database -d $db -v">>$LOG 2>&1
		EE
		su - $crs_user -c "srvctl config database -d $db -a">>$LOG 2>&1
		if [[ $db_num -gt 1 ]];then PP "-" "90";((db_num=db_num-1));fi
	 fi
	done
	if [[ -z $isnull ]];then P;fi
	P_BOT
	Runcrsctl "$crs_user" "crsctl query css votedisk"
	Runcrsctl "$crs_user" "ocrcheck"
	Runcrsctl "$crs_user" "ocrconfig -showbackup"
 fi

 if [[ $CHK_ASM = "Y" ]];then
	RunASMsql '$' 'srvctl status asm' 'srvctl status asm'
	RunASMsql 'N' 'lsdg' 'asmcmd lsdg'
	RunASMsql 'Y' "select instance_number inst_num,instance_name inst_name,host_name,version,to_char(startup_time,'yyyymmddhh24miss') startup_time,status,parallel,archiver,logins,database_status,active_state,blocked from v\$instance;" "
	col inst_num for a8
	col inst_name for a12
	col host_name for a12
	col version for a12
	col startup_time for a15
	col status for a10
	col parallef for a10
	col archiver for a10
	col logins for a10
	col database_status for a15
	col active_state for a12
	col blocked for a10
	select trim(instance_number) inst_num,instance_name inst_name,host_name,version,to_char(startup_time,'yyyymmddhh24miss') startup_time,status,parallel,archiver,logins,database_status,active_state,blocked " 'from v\$instance;'
	RunASMsql 'Y' 'select group_number,disk_number,name,failgroup,mount_status,header_status,state,total_mb,free_mb,total_mb-free_mb used_mb,create_date,repair_timer,preferred_read,path from v$asm_disk order by group_number,failgroup,disk_number;' '
	col grp_num for a7
	col dsk_num for a7
	col name for a14
	col failgroup for a14
	col mount_status for a12
	col header_status for a13
	col state for a8
	col total_mb for a8
	col free_mb for a7
	col used_mb for a7
	col path for a30
	col rep_time for a8
	col create_date for a11
	col pre_read for a8
	select trim(group_number) GRP_NUM,trim(disk_number) DSK_NUM,name,failgroup,mount_status,header_status,state,trim(total_mb) TOTAL_MB,trim(free_mb) FREE_MB,trim(total_mb-free_mb) USED_MB,' "to_char(create_date,'yyyymmddhh24') CREATE_DATE," 'trim(repair_timer) REP_TIME,preferred_read PRE_READ,path from v\$asm_disk order by group_number,failgroup,disk_number;'
	RunASMsql 'Y' 'select group_number,name,state,type,total_mb,free_mb,total_mb-free_mb USED_MB,usable_file_mb,required_mirror_free_mb,offline_disks from v$asm_diskgroup order by group_number;' '
	col group_num for a9
	col name for a15
	col state for a15
	col type for a10
	col total_mb for a9
	col free_mb for a8
	col used_mb for a8
	col usable_file_mb for a15
	col required_mirror_free_mb for a24
	col offline_disks for a13
	select trim(group_number) GROUP_NUM,name,state,type,trim(total_mb) TOTAL_MB,trim(free_mb) FREE_MB,trim(total_mb-free_mb) USED_MB,trim(usable_file_mb) USABLE_FILE_MB,trim(required_mirror_free_mb) REQUIRED_MIRROR_FREE_MB,trim(offline_disks) OFFLINE_DISKS from v\$asm_diskgroup order by group_number;'
	RunASMsql 'Y' 'show parameter' '
	col type_col_plus_show_param for a15
	col value_col_plus_show_param for a80
	show parameter'
 fi

 instance_name=`ps -ef|grep smon|egrep -v grep|awk '{print $NF}'|awk 'sub("ora_smon_","",$NF) {print $NF}'|sed -e 's/(//g' -e 's/)//g'`
 CHECK_CON=0
 for db_name in $instance_name;do
	((CHECK_CON=CHECK_CON+1))
	if [[ $CHECK_CON -lt 2 ]];then
	 #版本
	 Runsql 'Y' 'select * from v$version;' '
	 set line 150
	 col banner for a80
	 select * from v\$version;'
	 #组件
	 Runsql 'Y' 'select comp_id,comp_name,version,status from dba_registry;' '
	 col comp_id for A10
	 col comp_name for A40
	 col version for A14
	 col status for A10
	 select comp_id,comp_name,version,status from dba_registry;'
	 #补丁
	 if [[ $CHK_OPATCH = "Y" ]];then
		if [[ -f /etc/sysconfig/i18n ]];then
		 mv /etc/sysconfig/i18n /etc/sysconfig/i18n.TianYi
		 cat /etc/sysconfig/i18n.TianYi > /etc/sysconfig/i18n
		 $E 'LANG="zh_CN.UTF-8:en_US.UTF-8:en_US:en"' >> /etc/sysconfig/i18n
		fi
		if [[ $crs_user = "grid" ]];then Runsql 'N' 'grid' '' "$GRID_HOME/OPatch/opatch lsinventory -all";fi
		Runsql 'N' 'oracle' '' "$ORA_HOME/OPatch/opatch lsinventory -all"
		if [[ -f /etc/sysconfig/i18n.TianYi ]];then
		 cat /etc/sysconfig/i18n.TianYi > /etc/sysconfig/i18n
		fi
	 fi
	fi
	#实例
	Runsql 'Y' 'select instance_number,instance_name,parallel,status,database_status,active_state,host_name from gv$instance order by inst_id;' '
	col instance_id for a12
	col instance_name for a14
	col parallel for a10
	col status for a10
	col database_status for a16
	col active_state for a14
	col host_name for a15
	select trim(instance_number) "INSTANCE_ID",instance_name,parallel,status,database_status,active_state,host_name from gv\$instance order by inst_id;'
	#字符集
	Runsql 'Y' "select userenv('language') LANGUAGE from dual;" "select userenv('language') LANGUAGE from dual;"
	#SGA
	Runsql 'Y' 'show parameter sga;' '
	col name_col_plus_show_param for a22
	col value_col_plus_show_param for a10
	show parameter sga;'
	#PGA
	Runsql 'Y' 'select pga_target_for_estimate/1024/1024 "PGA(MB)",pga_target_factor,estd_pga_cache_hit_percentage,estd_overalloc_count from v$pga_target_advice;' '
	col name_col_plus_show_param for a22
	col value_col_plus_show_param for a10
	col PGA(MB) for a15
	col PGA_TARGET_FACTOR for a20
	col ESTD_PGA_CACHE_HIT_PERCENTAGE for a31
	col ESTD_OVERALLOC_COUNT for a22
	show parameter pga;
	set head off
	select'" '======================================================================================' "'from dual;
	set head on
	select trim(to_char(pga_target_for_estimate/1024/1024,'"'FM99999990.0'"')) "PGA(MB)",trim(to_char(pga_target_factor,'"'FM99990.0'"')) PGA_TARGET_FACTOR,trim(estd_pga_cache_hit_percentage) ESTD_PGA_CACHE_HIT_PERCENTAGE,trim(estd_overalloc_count) ESTD_OVERALLOC_COUNT from v\$pga_target_advice;'
	#参数
	Runsql 'Y' 'show parameter spfile;' '
	col name_col_plus_show_param for a10
	col value_col_plus_show_param for a80
	show parameter spfile;'
	Runsql 'Y' "show parameter" "
	col type_col_plus_show_param for a15
	col value_col_plus_show_param for a80
	show parameter"
	#归档模式
	Runsql 'Y' 'archive log list;' 'archive log list;'
	#控制文件
	Runsql 'Y' 'select * from v$controlfile;' '
	col name for a60
	col is_recovery_dest_file for a22
	select * from v\$controlfile;'
	#redolog
	Runsql 'Y' 'select l.thread#,f.group#,f.type,l.status,l.bytes/1024/1024 "SIZE(MB)",f.member from v$logfile f,v$log l where f.group#=l.group# order by l.thread#,f.group#;' '
	col member for a60
	col THREAD_ID for a10
	col GROUP_ID for a9
	col STATUS for a10
	col SIZE(MB) for a10
	select trim(l.thread#) "THREAD_ID",trim(f.group#) "GROUP_ID",f.type,l.status,trim(l.bytes/1024/1024) "SIZE(MB)",f.member from v\$logfile f,v\$log l where f.group#=l.group# order by l.thread#,f.group#;'
	#redo log切换频率
	Runsql 'Y' "select to_char(first_time,'yyyymmdd') DAY,count(*) sw_cnt,from v\$log_history where first_time > trunc(sysdate - 10) group by rollup(to_char(first_time,'yyyy-mm-dd'));" '
	col h00 for 9999 heading H00
	col h01 for 9999 heading H01
	col h02 for 9999 heading H02
	col h03 for 9999 heading H03
	col h04 for 9999 heading H04
	col h05 for 9999 heading H05
	col h06 for 9999 heading H06
	col h07 for 9999 heading H07
	col h08 for 9999 heading H08
	col h09 for 9999 heading H09
	col h10 for 9999 heading H10
	col h11 for 9999 heading H11
	col h12 for 9999 heading H12
	col h13 for 9999 heading H13
	col h14 for 9999 heading H14
	col h15 for 9999 heading H15
	col h16 for 9999 heading H16
	col h17 for 9999 heading H17
	col h18 for 9999 heading H18
	col h19 for 9999 heading H19
	col h20 for 9999 heading H20
	col h21 for 9999 heading H21
	col h22 for 9999 heading H22
	col h23 for 9999 heading H23
	col DAY for a8 heading DATE
	col sw_cnt for 99999 heading COUNT
	col Mb for 999999999 heading SIZE(MB)
	var redoMbytes number;
	begin
	select max(bytes)/1024/1024 into :redoMbytes from v\$log;
	end;
	/
	select ' "to_char(first_time,'yyyymmdd') DAY, " 'count(*) sw_cnt,count(*) * :redoMbytes Mb, ' "
	SUM (DECODE (TO_CHAR (first_time, 'hh24'), '00', 1, 0)) h00,
	SUM (DECODE (TO_CHAR (first_time, 'hh24'), '01', 1, 0)) h01,
	SUM (DECODE (TO_CHAR (first_time, 'hh24'), '02', 1, 0)) h02,
	SUM (DECODE (TO_CHAR (first_time, 'hh24'), '03', 1, 0)) h03,
	SUM (DECODE (TO_CHAR (first_time, 'hh24'), '04', 1, 0)) h04,
	SUM (DECODE (TO_CHAR (first_time, 'hh24'), '05', 1, 0)) h05,
	SUM (DECODE (TO_CHAR (first_time, 'hh24'), '06', 1, 0)) h06,
	SUM (DECODE (TO_CHAR (first_time, 'hh24'), '07', 1, 0)) h07,
	SUM (DECODE (TO_CHAR (first_time, 'hh24'), '08', 1, 0)) h08,
	SUM (DECODE (TO_CHAR (first_time, 'hh24'), '09', 1, 0)) h09,
	SUM (DECODE (TO_CHAR (first_time, 'hh24'), '10', 1, 0)) h10,
	SUM (DECODE (TO_CHAR (first_time, 'hh24'), '11', 1, 0)) h11,
	SUM (DECODE (TO_CHAR (first_time, 'hh24'), '12', 1, 0)) h12,
	SUM (DECODE (TO_CHAR (first_time, 'hh24'), '13', 1, 0)) h13,
	SUM (DECODE (TO_CHAR (first_time, 'hh24'), '14', 1, 0)) h14,
	SUM (DECODE (TO_CHAR (first_time, 'hh24'), '15', 1, 0)) h15,
	SUM (DECODE (TO_CHAR (first_time, 'hh24'), '16', 1, 0)) h16,
	SUM (DECODE (TO_CHAR (first_time, 'hh24'), '17', 1, 0)) h17,
	SUM (DECODE (TO_CHAR (first_time, 'hh24'), '18', 1, 0)) h18,
	SUM (DECODE (TO_CHAR (first_time, 'hh24'), '19', 1, 0)) h19,
	SUM (DECODE (TO_CHAR (first_time, 'hh24'), '20', 1, 0)) h20,
	SUM (DECODE (TO_CHAR (first_time, 'hh24'), '21', 1, 0)) h21,
	SUM (DECODE (TO_CHAR (first_time, 'hh24'), '22', 1, 0)) h22,
	SUM (DECODE (TO_CHAR (first_time, 'hh24'), '23', 1, 0)) h23 " '
	from v\$log_history where first_time > trunc(sysdate - 10) ' "group by rollup(to_char(first_time,'yyyymmdd'));"
	#归档日志
	Runsql 'Y' 'select thread#,sequence#,name,to_char(blocks*block_size/1024/1024,'FM99990.09') "SIZE(MB)",completion_time "END_TIME",archived,applied,deleted from v$archived_log where rownum < 100 order by sequence# desc;' '
	col THREAD for 99999999
	col THREAD for a6
	col SEQUENCE for 99999999
	col SEQUENCE for a8
	col name for a70
	col SIZE(MB) for a8
	col END_TIME for a14
	col archived for a8
	col deleted for a7
	col applied for a7
	select trim(thread#) "THREAD",trim(sequence#) "SEQUENCE",name,trim(to_char(blocks*block_size/1024/1024,' "'FM99990.09'))" '"SIZE(MB)",to_char(completion_time,'"'yyyymmddhh24miss')"' "END_TIME",archived,applied,deleted from v\$archived_log where rownum < 100 order by sequence# desc;'
	#表空间
	Runsql 'Y' 'select a.a1 "TABLESPACE_NAME",c.c3 "STATUS",c.c2 "TYPE",trim(to_char(b.b2/1024/1024,'99999999999999')) "TOTAL_SIZE(MB)",trim(to_char((b.b2-a.a2)/1024/1024,'99999999999999')) "USE_SIZE(MB)",substr((b.b2-a.a2)/b.b2*100,1,5) "USE(%)" from (select tablespace_name a1, sum(nvl(bytes,0)) a2 from dba_free_space group by tablespace_name) a,(select tablespace_name b1,sum(bytes) b2 from dba_data_files group by tablespace_name) b,(select tablespace_name c1,contents c2,status c3 from dba_tablespaces) c where a.a1=b.b1 and c.c1=b.b1 order by 1;' '
	col TABLESPACE_NAME for a30
	col TYPE for a15
	col TOTAL_SIZE(MB) for a15
	col USE_SIZE(MB) for a13
	col USE(%) for a7
	select a.a1 "TABLESPACE_NAME",c.c3 "STATUS",c.c2 "TYPE",'"trim(to_char(b.b2/1024/1024,'99999999999999')) "'"TOTAL_SIZE(MB)",trim(to_char((b.b2-a.a2)/1024/1024,'"'99999999999999')) "'"USE_SIZE(MB)",'"trim(to_char(substr((b.b2-a.a2)/b.b2*100,1,5),'FM990.099')) "'"USE(%)" from (select tablespace_name a1, sum(nvl(bytes,0)) a2 from dba_free_space group by tablespace_name) a,(select tablespace_name b1,sum(bytes) b2 from dba_data_files group by tablespace_name) b,(select tablespace_name c1,contents c2,status c3 from dba_tablespaces) c where a.a1=b.b1 and c.c1=b.b1 order by 1;'
	#临时表空间
	Runsql 'Y' 'select a.tablespace_name "TABLESPACE_NAME",(b.bytes)/1024/1024 "SIZE(MB)",b.status,b.autoextensible,b.file_name "TEMPORARY_DATAFILE_NAME" from dba_tablespaces a,dba_temp_files b where a.tablespace_name=b.tablespace_name and a.contents='TEMPORARY' order by a.tablespace_name;' '
	col tablespace_name for a25
	col SIZE(MB) for a8
	col status for a10
	col autoextensible for a15
	col temporary_datafile_name for a70
	select a.tablespace_name "TABLESPACE_NAME",trim((b.bytes)/1024/1024) "SIZE(MB)",b.status,b.autoextensible,b.file_name "TEMPORARY_DATAFILE_NAME" from dba_tablespaces a,dba_temp_files b where a.tablespace_name=b.tablespace_name and a.contents='"'TEMPORARY' order by a.tablespace_name;"
	#数据文件使用
	Runsql 'Y' 'select file# "ID",name,BYTES/1024/1024 "SIZE(MB)",status,enabled,online_time,LAST_TIME,LAST_CHANGE# from v$datafile;' '
	col id for a4
	col name for a70
	column size(mb) for 9,999,999 heading SIZE(MB)
	col size(mb) for a9
	col status for a10
	col enabled for a10
	col online_time for a12
	col last_time for a12
	col last_change for a12
	select trim(file#) "ID",'"name,trim(to_char(BYTES/1024/1024,'999999999')) "'"SIZE(MB)",status,enabled,to_char(online_time,'"'yyyymmddhh24mi') ONLINE_TIME,to_char(LAST_TIME,'yyyymmddhh24mi') LAST_TIME"',trim(LAST_CHANGE#) "LAST_CHANGE" from v\$datafile;'
	Runsql 'Y' 'select b.file_id "ID",b.file_name "DATAFILE_NAME",b.tablespace_name "TABLESPACE_NAME",to_char((b.bytes)/1024/1024,'FM9999990.0') "TOTAL_SIZE(MB)",to_char((b.bytes-sum(nvl(a.bytes,0)))/1024/1024,'FM9999990.0') "USE_SIZE(MB)",substr((b.bytes-sum(nvl(a.bytes,0)))/(b.bytes)*100,1,5) "USE(%)",b.status,b.autoextensible "AUTOEXT",to_char(b.increment_by*&blksz/(1024*1024),99999.9) "INC(MB)",to_char(b.maxbytes/1024/1024,9999999.9) "MAX(MB)" from dba_free_space a,dba_data_files b where a.file_id=b.file_id group by b.tablespace_name,b.file_name,b.bytes,b.status,b.autoextensible,b.increment_by,b.maxbytes order by b.tablespace_name;' '
	col ID for a4
	col DATAFILE_NAME for a65
	col TABLESPACE_NAME for a25
	col USE_SIZE(MB) for a12
	col TOTAL_SIZE(MB) for a14
	col USE(%) for a6
	col AUTOEXT for a7
	col INC(MB) for a7
	col MAX(MB) for a9
	col status for a10
	var blksz number;
	begin
	select value db_block_size into :blksz from v\$parameter ' "where name='db_block_size';" '
	end;
	/
	select trim(b.file_id) "ID",b.file_name "DATAFILE_NAME",b.tablespace_name "TABLESPACE_NAME",trim(to_char((b.bytes)/1024/1024,'"'FM9999990.0'"')) "TOTAL_SIZE(MB)",trim(to_char((b.bytes-sum(nvl(a.bytes,0)))/1024/1024,'"'FM9999990.0'"')) "USE_SIZE(MB)",trim(to_char(substr((b.bytes-sum(nvl(a.bytes,0)))/(b.bytes)*100,1,5),'"'FM990.09'"')) "USE(%)",b.status,b.autoextensible "AUTOEXT",trim(to_char(b.increment_by*:blksz/(1024*1024),'"'FM99990.0'"')) "INC(MB)",trim(to_char(b.maxbytes/1024/1024,'"'FM9999990.0'"')) "MAX(MB)" from dba_free_space a,dba_data_files b where a.file_id=b.file_id group by b.tablespace_name,b.file_name,b.file_id,b.bytes,b.status,b.autoextensible,b.increment_by,b.maxbytes order by b.tablespace_name;'
	#datafiles总量
	Runsql 'Y' 'select count(*) "DATAFILE_COUNT",sum(bytes)/1024/1024 "TOTAL_SIZE(MB)" from v$datafile;' '
	col DATAFILE_COUNT for a15
	col TOTAL_SIZE(MB) for a15
	select trim(count(*)) "DATAFILE_COUNT",'"trim(to_char(sum(bytes)/1024/1024,'FM999999999990.09')) "'"TOTAL_SIZE(MB)" from v\$datafile;'
	#segments总量
	Runsql 'Y' 'select count(*) "DATAFILE_COUNT",sum(bytes)/1024/1024 "TOTAL_SIZE(MB)" from dba_segments;' '
	col datafile_count for a15
	col TOTAL_SIZE(MB) for a15
	select trim(count(*)) "DATAFILE_COUNT",'"trim(to_char(sum(bytes)/1024/1024,'FM999999999990.09')) "'"TOTAL_SIZE(MB)" from dba_segments;'
	#resource_limit
	Runsql 'Y' 'select * from v$resource_limit;' '
	set line 400
	col resource_name for 999999
	col CURRENT_UTILIZATION for 999999
	col MAX_UTILIZATION for 99999999
	col INITIAL_ALLOCATION for a10
	col LIMIT_VALUE for a10
	select * from v\$resource_limit;'
	#是否配置dataguard
	Runsql 'Y' 'select name,dbid,protection_mode,protection_level,log_mode,remote_archive,database_role,dataguard_broker,guard_status,force_logging from v$database;' '
	col name for a10
	col dbid for a11
	col protection_mode for a20
	col protection_level for a20
	col log_mode for a14
	col remote_archive for a14
	col database_role for a14
	col dataguard_broker for a16
	col guard_status for a12
	col force_logging for a13
	select name,trim(dbid) "DBID",protection_mode,protection_level,log_mode,remote_archive,database_role,dataguard_broker,guard_status,force_logging from v\$database;'
	#用户及密码
	Runsql 'Y' 'select a.username,b.password,a.account_status,a.default_tablespace,a.temporary_tablespace,a.created from dba_users a,user$ b where a.user_id=b.user# order by a.username;' '
	col username for a30
	col password for a36
	col account_status for a17
	col default_tablespace for a25
	col temporary_tablespace for a25
	col created for a12
	select a.username,b.password,a.account_status,a.default_tablespace,a.temporary_tablespace,'"to_char(a.created,'yyyymmddhh24mi') CREATED"' from dba_users a,user\$ b where a.user_id=b.user# order by a.username;'
	#Shared Pool Size 命中率
	Runsql 'Y' 'select round((sum(gets)-sum(reloads))/sum(gets)*100,1) "libiary cache hit ratio %" from v$librarycache where namespace in(SQL AREA,TABLE/PROCEDURE,BODY,TRIGGER);' '
	col "LIBIARY CACHE HIT RATIO" for a25
	select trim(to_char(round((sum(gets)-sum(reloads))/sum(gets)*100,1),'"'FM990.099'"'))||' "' %'" '"LIBIARY CACHE HIT RATIO" from v\$librarycache ' "where namespace in('SQL AREA','TABLE/PROCEDURE','BODY','TRIGGER');"
	#数据缓冲区命中率
	Runsql 'Y' 'select round((1-(phy.value/(cur.value+con.value)))*100,1)||'%' ratio from v$sysstat phy,v$sysstat cur,v$sysstat con where phy.name=physical reads and cur.name=db block gets and con.name=consistent gets;' '
	col "DATA BUFFER HIT RATIO" for a25
	select trim(to_char(round((1-(phy.value/(cur.value+con.value)))*100,1),'"'FM990.099'"'))||' "' %'" '"DATA BUFFER HIT RATIO" from v\$sysstat phy,v\$sysstat cur,v\$sysstat con ' "where phy.name='physical reads' and cur.name='db block gets' and con.name='consistent gets';"
	#数据字典命中率
	Runsql 'Y' 'select round((1-sum(getmisses)/sum(gets))*100,1) "data dictionary hit ratio %" from v$rowcache;' '
	col "DATA DICTIONARY HIT RATIO" for a25
	select trim(to_char(round((1-sum(getmisses)/sum(gets))*100,1),'"'FM990.099'"'))||' "' %'" '"DATA DICTIONARY HIT RATIO" from v\$rowcache;'
	#排序命中率
	Runsql 'Y' 'select a.value "Sort(Disk)",b.value "Sort(Memory)",round(100*(a.value/decode((a.value+b.value), 0,1,(a.value+b.value))),2) "% Ratio (STAY UNDER 5%)" from v$sysstat a,v$sysstat b where a.name = sorts (disk) and b.name = sorts (memory);' '
	col sort(disk) for a14
	col sort(memory) for a14
	col "RATIO(STAY UNDER 5%)" for a22
	select trim(a.value) "SORT(DISK)",trim(b.value) "SORT(MEMORY)",trim(to_char(round(100*(a.value/decode((a.value+b.value), 0,1,(a.value+b.value))),2),'"'FM990.099'"'))||' "' %'" '"RATIO(STAY UNDER 5%)" from v\$sysstat a,v\$sysstat b ' "where a.name = 'sorts (disk)' and b.name = 'sorts (memory)';"
	#redo log buffer retry ratio
	Runsql 'Y' 'select to_char(r.value/e.value) "REDO RETRY RATIO(UNDER 5%)" from v$sysstat r,v$sysstat e where r.name=redo buffer allocation retries and e.name=redo entries;' '
	col "REDO RETRY RATIO(UNDER 5%)" for a28
	select trim(to_char(round((r.value/e.value)*100,2),'"'FM990.099')) || ' %'"' "REDO RETRY RATIO(UNDER 5%)" ' 'from v\$sysstat r,v\$sysstat e ' "where r.name='redo buffer allocation retries' and e.name='redo entries';"
	#锁竞争率
	Runsql 'Y' 'select substr(ln.name,1,25) Name,l.gets,l.misses,100*(l.misses/l.gets) "% Ratio(UNDER 1%)" from v$latch l,v$latchname ln where ln.name in(cache buffers lru chain) and ln.latch# = l.latch#;' '
	col name for a40
	col "RATIO(STAY UNDER 1%)" for a22
	col gets for a12
	col misses for a12
	select substr(ln.name,1,40) Name,trim(l.gets) "GETS",trim(l.misses) "MISSES",trim(to_char(100*(l.misses/l.gets),'"'FM990.099'))|| ' %'" '"RATIO(STAY UNDER 1%)" from v\$latch l,v\$latchname ln ' "where ln.name in ('cache buffers lru chain') and ln.latch# = l.latch#;"
	#是否起用flashback
	Runsql 'Y' 'select flashback_on from v$database;' '
	col flashback_on for a13
	select flashback_on from v\$database;'
	#数据库链接
	Runsql 'Y' 'select * from dba_db_links;' '
	col HOST for a55
	col OWNER for a25
	col DB_LINK for a50
	col USERNAME for a20
	select * from dba_db_links;'
	#自动任务
	Runsql 'Y' "select owner,job_type,job_name,state,enabled,start_date,next_run_date,last_start_date,run_count,failure_count from dba_scheduler_jobs;" "
	col owner for a12
	col job_type for a16
	col job_name for a30
	col state for a10
	col enabled for a8
	col start_date for a14
	col next_run_date for a14
	col last_start_date for a14
	col run_count for a9
	col failure_count for a13
	select owner,job_type,job_name,state,enabled,to_char(start_date,'yyyymmddhh24miss') START_DATE,to_char(next_run_date,'yyyymmddhh24miss') NEXT_RUN_DATE,to_char(last_start_date,'yyyymmddhh24miss') LAST_START_DATE,trim(run_count) RUN_COUNT,trim(failure_count) FAILURE_COUNT from dba_scheduler_jobs;"
	#作业
	Runsql 'Y' "select JOB  ID,LOG_USER SUBMITTER,PRIV_USER SECURITY,WHAT JOB,to_char(LAST_DATE,'yyyymmddhh24mi') LAST_DATE,to_char(NEXT_DATE,'yyyymmddhh24mi') NEXT_RUN,trim(FAILURES) FAILURES,decode(BROKEN,'Y','N','Y') OK from sys.dba_jobs;" "
	col job_id for a6
	col job for a70 truncate
	col ok for a2
	col submitter for a15 truncate
	col security for a15 truncate
	col last_date for a12
	col next_run for a12
	col failures for a8
	select trim(JOB) JOB_ID,LOG_USER SUBMITTER,PRIV_USER SECURITY,WHAT JOB,to_char(LAST_DATE,'yyyymmddhh24mi') LAST_DATE,to_char(NEXT_DATE,'yyyymmddhh24mi') NEXT_RUN,trim(FAILURES) FAILURES,decode(BROKEN,'Y','N','Y') OK from sys.dba_jobs;"
	#会话数
	Runsql 'Y' 'select count(*) from gv$session where status=ACTIVE;' '
	col session_count for a15
	select trim(count(*)) "SESSION_COUNT" from gv\$session ' "where status='ACTIVE';"
	#会话等待数
	Runsql 'Y' 'select count(*) total_in_wait from v$session_wait where event=log buffer space;' '
	col total_in_wait for a15
	select trim(count(*)) "TOTAL_IN_WAIT" from v\$session_wait ' "where event='log buffer space';"
	#Top CPU users
	Runsql 'Y' 'select a.INST_ID,ROWNUM as RANK,a.SID,a.USERNAME,a.OSUSER,a.MACHINE,a.PROGRAM,a.CPUMINS from (select v.INST_ID,v.SID,USERNAME,OSUSER,MACHINE,PROGRAM,round(v.VALUE/(100*60),0) CPUMINS from gv$statname s ,gv$sesstat v,gv$session sess where s.NAME=CPU used by this session and sess.SID=v.SID and v.STATISTIC#=s.STATISTIC# and v.VALUE > 0 order by v.VALUE desc) a where rownum < 11;' '
	col inst_id for a8
	col osuser for a10
	col username for a10
	col machine for a30 truncate
	col rank for a5
	col sid for a5
	col program for a40 truncate
	col cpumins for a10
	select trim(a.INST_ID) "INST_ID",trim(ROWNUM) as RANK,trim(a.SID) "SID",a.USERNAME,a.OSUSER,a.MACHINE,a.PROGRAM,trim(a.CPUMINS) "CPUMINS" from (select v.INST_ID,v.SID,USERNAME,OSUSER,MACHINE,PROGRAM,round(v.VALUE/(100*60),0) CPUMINS from gv\$statname s ,gv\$sesstat v,gv\$session sess ' "where s.NAME='CPU used by this session' and sess.SID=v.SID and v.STATISTIC#=s.STATISTIC# and v.VALUE > 0 order by v.VALUE desc) a where rownum < 11;"
	#无效对象
	Runsql 'Y' "select owner,object_name,object_type,status,last_ddl_time from dba_objects where status like 'INVALID';" "
	col owner for a30
	col object_type for a15
	col status for a10
	col object_name for a60
	col last_ddl_time for a14
	select owner,object_name,object_type,status,to_char(last_ddl_time,'yyyymmddhh24miss') LAST_DDL_TIME from dba_objects where status like 'INVALID';
	select owner,count(*) from dba_objects where status='INVALID' group by owner;"
	#DBA用户权限
	Runsql 'Y' "select * from dba_role_privs where granted_role='DBA';" "
	col admin_option for a12
    col default_role for a12
    select * from dba_role_privs where granted_role='DBA';"
	#spfile内容
	Runsql "N_Spfile" "$db_name" "pfile.ora"
	#rman_configuration
	Runsql 'Y' 'select * from v$rman_configuration;' '
	col name for a40
	col value for a60
	select * from v\$rman_configuration;'
	#Last 10 RMAN Backup Jobs Info
	Runsql 'Y' "RMAN Backup Jobs Info" "
	set line 400
    col  command_id   for a15
    col backup_name for a20
    col  start_time  for a20
    col  elapsed_time for a15
    col  status for a10
    col  input_type for a10
    col  output_device_type for a10
    col  input_size for a10
    col  output_size for a10
    col  output_rate_per_sec for a20
    SELECT
        r.command_id  backup_name
      , TO_CHAR(r.start_time, 'yyyymmdd hh24:mi')  start_time 
      , r.time_taken_display    elapsed_time 
      , r.status  status
      , r.input_type  input_type
      , r.output_device_type output_device_type
      ,  r.input_bytes_display input_size
      ,  r.output_bytes_display  output_size
      ,  r.output_bytes_per_sec_display  output_rate_per_sec
        FROM 
         " '(select
               command_id
             , start_time
             , time_taken_display
             , status
             , input_type
             , output_device_type
             , input_bytes_display
             , output_bytes_display
             , output_bytes_per_sec_display
           from v\$rman_backup_job_details
           order by start_time DESC
          ) r
       WHERE
       rownum < 11' ";"
	#当前数据库内锁定对象及其信息
	Runsql "Y" "lock object info" "
	set line 500
	col sid for 9999
	col serial# for 9999
	col username for a15
    col OS_USER_NAME for a20
    col OBJECT_OWNER for a20
    col OBJECT_NAME for a40
    col LOCKED_MODE for a15
	SELECT LO.SESSION_ID AS SID,
       S.SERIAL#,
       NVL(LO.ORACLE_USERNAME, '(oracle)') AS USERNAME,
       O.OWNER AS OBJECT_OWNER,
       O.OBJECT_NAME,
       DECODE(LO.LOCKED_MODE,
              0,'None',
              1,'Null (NULL)',
              2,'Row-S (SS)',
              3,'Row-X (SX)',
              4,'Share (S)',
              5,'S/Row-X (SSX)',
              6,'Exclusive (X)',
              LO.LOCKED_MODE) LOCKED_MODE,LO.OS_USER_NAME 
      FROM " 'V\$LOCKED_OBJECT LO  JOIN DBA_OBJECTS O  ON O.OBJECT_ID=LO.OBJECT_ID  JOIN V\$SESSION  S  ON LO.SESSION_ID=S.SID  ORDER BY 1, 2, 3, 4' ";"
	##SELECT LO.SESSION_ID AS SID,S.SERIAL#,NVL(LO.ORACLE_USERNAME, '(oracle)') AS USERNAME,O.OWNER AS OBJECT_OWNER,O.OBJECT_NAME,DECODE(LO.LOCKED_MODE,0,'None',1,'Null (NULL)',2,'Row-S (SS)',3,'Row-X (SX)',4,'Share (S)',5,'S/Row-X (SSX)',6,'Exclusive (X)',LO.LOCKED_MODE) LOCKED_MODE,LO.OS_USER_NAME  FROM V$LOCKED_OBJECT LO  JOIN DBA_OBJECTS O  ON O.OBJECT_ID = LO.OBJECT_ID  JOIN V$SESSION S  ON LO.SESSION_ID = S.SID ORDER BY 1, 2, 3, 4;
	#最近一天等待事件列表
	Runsql 'Y' "wait events last 1 day" "
	col time for a30
    col event for a50
    select to_char(sample_time,'yyyymmdd hh24:mi') time,event,count(*) from dba_hist_active_sess_history where sample_time> trunc((sysdate-1)) and sample_time<=trunc((sysdate+1)) group by to_char(sample_time,'yyyymmdd hh24:mi'),event order by 3 desc;"
	#Last spfile copies
	Runsql 'Y' 'select * from (select bp.DEVICE_TYPE,sp.SPFILE_INCLUDED SPFILE_INCLUDED,bs.COMPLETION_TIME,decode(STATUS,A,Available,D,Deleted,X,Expired) STATUS,HANDLE HANDLE from v$backup_set bs,v$backup_piece bp,(select distinct SET_STAMP,SET_COUNT,YES SPFILE_INCLUDED from v$backup_spfile) sp where bs.SET_STAMP = bp.SET_STAMP and bs.SET_COUNT = bp.SET_COUNT and bp.STATUS in (A) and bs.SET_STAMP = sp.SET_STAMP and bs.SET_COUNT = sp.SET_COUNT order by bs.RECID desc,PIECE#) where rownum < 20;' "
	col device_type for a12
	col spfile_included for a15
	col completion_time for a15
	col status for a12
	col handle for a80 truncate
	select * from (select bp.DEVICE_TYPE,sp.SPFILE_INCLUDED SPFILE_INCLUDED,to_char(bs.COMPLETION_TIME,'yyyymmddhh24miss') COMPLETION_TIME,decode(STATUS,'A','Available','D','Deleted','X','Expired') STATUS,HANDLE HANDLE " 'from v\$backup_set bs,v\$backup_piece bp, ' "(select distinct SET_STAMP,SET_COUNT,'YES' SPFILE_INCLUDED " 'from v\$backup_spfile) sp where bs.SET_STAMP = bp.SET_STAMP and bs.SET_COUNT = bp.SET_COUNT ' "and bp.STATUS in ('A') and bs.SET_STAMP = sp.SET_STAMP and bs.SET_COUNT = sp.SET_COUNT order by bs.RECID desc,PIECE#) where rownum < 20;"
	#Last controlfile copies
	Runsql 'Y' 'select * from (select bp.device_type,decode(bs.CONTROLFILE_INCLUDED,NO,-,bs.CONTROLFILE_INCLUDED) CONTROLFILE_INCLUDED,bs.COMPLETION_TIME,decode(STATUS,A,Available,D,Deleted,X,Expired) STATUS,HANDLE HANDLE from v$backup_set bs,v$backup_piece bp where bs.SET_STAMP = bp.SET_STAMP and bs.SET_COUNT=bp.SET_COUNT and bp.STATUS in (A) and bs.CONTROLFILE_INCLUDED != NO order by bs.RECID desc,PIECE#) where rownum < 20;' "
	col device_type for a12
	col completion_time for a15
	col status for a12
	col controlfile_included for a20
	col handle form a80 truncate
	select * from (select bp.device_type,decode(bs.CONTROLFILE_INCLUDED,'NO','-',bs.CONTROLFILE_INCLUDED) CONTROLFILE_INCLUDED,to_char(bs.COMPLETION_TIME,'yyyymmddhh24miss') COMPLETION_TIME,decode(STATUS,'A','Available','D','Deleted','X','Expired') STATUS,HANDLE HANDLE " 'from v\$backup_set bs,v\$backup_piece bp where bs.SET_STAMP = bp.SET_STAMP and bs.SET_COUNT=bp.SET_COUNT ' "and bp.STATUS in ('A') and bs.CONTROLFILE_INCLUDED != 'NO' order by bs.RECID desc,PIECE#) where rownum < 20;"
	#Create users
	Runsql 'Y' "SELECT DBMS_METADATA.GET_DDL('USER',U.USERNAME)||';'FROM DBA_USERS U WHERE USERNAME NOT IN ('ANONYMOUS','APEX_030200','APEX_PUBLIC_USER','APPQOSSYS','BI','CTXSYS','DBSNMP','DMSYS','DIP','EXFSYS','FLOWS_30000','FLOWS_FILES','HR','MDDATA','IX','MDSYS',
	'MGMT_VIEW','OE','OLAPSYS','ORACLE_OCM','ORDDATA','ORDPLUGINS','ORDSYS','OUTLN','OWBSYS','OWBSYS_AUDIT','PM','SCOTT','SH','SI_INFORMTN_SCHEMA',
	'SPATIAL_CSW_ADMIN_USR','SPATIAL_WFS_ADMIN_USR','SYS','SYSMAN','SYSTEM','TSMSYS','WMSYS','XDB','XS\$NULL') ORDER BY U.USERNAME;" "
	SELECT DBMS_METADATA.GET_DDL('USER',U.USERNAME)||';'"' "Create the users script:"'" FROM DBA_USERS U WHERE USERNAME NOT IN ('ANONYMOUS','APEX_030200','APEX_PUBLIC_USER','APPQOSSYS','BI','CTXSYS','DBSNMP','DMSYS','DIP','EXFSYS','FLOWS_30000','FLOWS_FILES','HR','MDDATA','IX','MDSYS','MGMT_VIEW','OE','OLAPSYS','ORACLE_OCM','ORDDATA','ORDPLUGINS','ORDSYS','OUTLN','OWBSYS','OWBSYS_AUDIT','PM','SCOTT','SH','SI_INFORMTN_SCHEMA','SPATIAL_CSW_ADMIN_USR','SPATIAL_WFS_ADMIN_USR','SYS','SYSMAN','SYSTEM','TSMSYS','WMSYS','XDB','XS"'\$NULL'"') ORDER BY U.USERNAME;"
	#Create tablespace
	Runsql 'Y' "SELECT DBMS_METADATA.GET_DDL('TABLESPACE',U.TABLESPACE_NAME)|| '; '  FROM DBA_TABLESPACES U WHERE TABLESPACE_NAME NOT IN ('DRSYS','TEMP','UNDOTBS1','USERS','SYSAUX','SYSTEM','XDB');" "
	SELECT DBMS_METADATA.GET_DDL('TABLESPACE',U.TABLESPACE_NAME)|| ';'"' "Create the tablespace script:"'" FROM DBA_TABLESPACES U WHERE TABLESPACE_NAME NOT IN ('DRSYS','TEMP','UNDOTBS1','USERS','SYSAUX','SYSTEM','XDB');"
	Runsql "N_Alert" "-1000 alert_${db_name}.log" "tail"
 done
 if [[ $crs_user = "grid" ]];then Runsql 'N' 'grid' 'cat' "$GRID_HOME/network/admin/listener.ora";else Runsql 'N' 'oracle' 'cat' "$ORA_HOME/network/admin/listener.ora";fi
 LSNLOG=`su - oracle -c "lsnrctl status|grep \"Listener Log File\""|awk '{print $4}'`
 Runsql "N_LSNLog" "-1000 $LSNLOG" "tail"
 Runsql 'N' 'oracle' 'cat' "$ORA_HOME/network/admin/tnsnames.ora"
 Runsql 'N' 'oracle' 'cat' ".bash_profile|awk 'NF'"
 if [[ `grep grid /etc/passwd` ]];then Runsql 'N' 'grid' 'cat' ".bash_profile|awk 'NF'";fi
fi
#Storage Foundation信息
if { [[ $CHK_SF = "Y" ]] && [[ `rpm -qa|grep VRTS|grep -v grep|grep -v VRTSpbx|wc -l` -gt 5 ]]; } then
 $E "Get storage foundation information....";HR;href=800;HREF
 OutputIsErr()
 {
	$1>${LOG}.log 2>&1
	isnull="N"
	while IFS= read -r line;do
	 $E "$line"|grep -q "$2"
	 if [[ $? -eq 0 ]];then isnull="";break;fi
	done < ${LOG}.log
	if [[ $isnull = "N" ]];then cmd "$1";else EE "$3";fi
	RM "${LOG}.log"
 }
 for command in "/opt/VRTS/bin/vxlicrep" "vxdisk -e -o alldgs list" "vxdg list" "vxdg free" "vxprint -vhtIP" "vxprint -htq" "vxprint -st" "vxstat -o alldgs -i 2 -c 8" "vxdmpadm listctlr all" "vxdmpadm listenclosure all" "vxdisk path" "vxdmpadm getsubpaths" "vxgetdmpnames" "vxdctl -c mode" "gabconfig -a" "hastatus -summary" "hares -state" "lltstat" "lltstat -n" "cat /etc/llttab" "cat /etc/VRTSvcs/conf/config/main.cf" "tail -200 /var/VRTSvcs/log/engine_A.log" "vxtask list" "vxsnap -g dg* -vx list";do
	which `$E $command|awk '{print $1}'`>/dev/null 2>&1
	if [[ $? -eq 0 ]];then
	 case $command in
		"vxdctl -c mode"|"gabconfig -a"|"hastatus -summary"|"hares -state"|"cat /etc/VRTSvcs/conf/config/main.cf"|"tail -200 /var/VRTSvcs/log/engine_A.log"|"lltstat"|"lltstat -n"|"cat /etc/llttab")
		 if [[ `rpm -q VRTSllt|wc -l` -gt 0 && `rpm -q VRTSvcs|wc -l` -gt 0 ]];then
			HREF;P_CMD "$command";P_TOP
			case $command in
			 "hares -state") OutputIsErr "$command" "No Resources" "No Resources are configured";;
			 "lltstat") OutputIsErr "$command" "No such file or directory" "No LLT are configured";;
			 "cat /etc/llttab") if [[ -e /etc/llttab ]];then cmd "$command";else EE "No LLT are configured";fi;;
			 "cat /etc/VRTSvcs/conf/config/main.cf"|"tail -200 /var/VRTSvcs/log/engine_A.log") P "$command" "OK";;
			 *) cmd "$command";;
			esac
			P_BOT;fi;;
		"vxtask list"|"vxdg list"|"vxdg free")
		 HREF;P_CMD "$command";P_TOP
		 if [[ $command = "vxtask list" ]];then
			if [[ `vxtask list|wc -l` -gt 1 ]];then cmd "$command";else EE "No active task.";fi
		 else
			if [[ `vxdisk list|egrep -v "-"|egrep -v "GROUP"|egrep -v grep|wc -l` -gt 0 ]];then cmd "$command";else EE "No diskgroup active.";fi
		 fi
		 P_BOT;;
		"vxsnap -g dg* -vx list")
		 HREF;P_CMD "$command" "N";P_TOP;SnapIsNull=""
		 for dg in `vxdg list|grep -v STATE|awk '{print $1}'`;do
			if [[ -n `vxsnap -g $dg -vx list` ]];then SnapIsNull="N";EE "#<b> vxsnap -g $dg -vx list</b>";cmd "vxsnap -g $dg -vx list";EE;fi
		 done
		 if [[ -z $SnapIsNull ]];then EE "All diskgroup no snapshot.";fi
		 P_BOT;;
		"vxstat -o alldgs -i 2 -c 8")
		 if [[ `vxdg list|wc -l` -gt 1 ]];then
			HREF;P_CMD "$command";P_TOP;vxstat -o alldgs>vxstat.$$ 2>&1
			if [[ -n `cat vxstat.$$|grep "vxstat ERROR"` ]];then
			 dg_num=`vxdg list|grep -v STATE|wc -l`
			 for dg in `vxdg list|grep -v STATE|awk '{print $1}'`;do
				EE "#<b> vxstat -g $dg -i 2 -c 8</b>";PP "-" "75";cmd "vxstat -g $dg -i 2 -c 8"
				if [[ $dg_num -gt 1 ]];then ((dg_num=dg_num-1));PP "-" "75";EE;fi
			 done
			else cmd "$command";fi
			RM "vxstat.$$"
			P_BOT;fi;;
		*)
		 HREF;P_CMD "$command";P_TOP
		 if [[ -z `$command` ]];then P;else cmd "$command";fi
		 P_BOT;;
	 esac
	fi
 done

 which vxprint vxtune vxrlink vxrvg vradmin>/dev/null 2>&1
 if [[ $? -eq 0 ]];then
	if [[ -n `vxprint -qV|grep "Disk group"|awk '{print $3}'` ]];then
	 HREF;P_CMD "vxtune";P_TOP;cmd "vxtune";P_BOT
	 for dg in `vxprint -qV|grep "Disk group"|awk '{print $3}'`;do
		HREF;P_CMD "$dg volume replicator information" "N";P_TOP;EE "#<b> vxprint -g $dg -VPl</b>";cmd "vxprint -g $dg -VPl"
		for rvg in `vxprint -g $dg -qVn`;do
		 EE "#<b> vxrlink -g $dg verify $rvg</b>";cmd "vxrlink -g $dg verify $rvg";EE
		 if [[ -f /etc/vx/vras/vras_env ]];then EE "#<b> vxrvg -g $dg stats $rvg</b>";cmd "vxrvg -g $dg stats $rvg";EE;fi
		 EE "#<b> vradmin -g $dg repstatus $rvg</b>";cmd "vradmin -g $dg repstatus $rvg";EE
		done
		rlink_num=`vxprint -g $dg -qPn|wc -l`
		for rlink in `vxprint -g $dg -qPn`;do
		 EE "#<b> vxrlink -T -g $dg status $rlink</b>";output_count=10
		 while [[ $output_count > 0 ]];do ((output_count=output_count-1));cmd "vxrlink -T -g $dg status $rlink";sleep 2;done
		 if [[ rlink_num -gt 1 ]];then ((rlink_num=rlink_num-1));EE;fi
		done
		P_BOT
	 done
	fi
 fi
fi
#NetBackup 信息
if { [[ $CHK_NBU = "Y" ]] && [[ -e "/usr/openv/netbackup" ]]; } then
 $E "Get NetBackup information....";HR;href=900;HREF
 for command in "cat /usr/openv/netbackup/bin/version" "cat /usr/openv/netbackup/bp.conf" "/usr/openv/netbackup/bin/admincmd/bpgetconfig" "/usr/openv/netbackup/bin/admincmd/bpminlicense -verbose" "/usr/openv/netbackup/bin/bpps -a" "/usr/openv/netbackup/bin/admincmd/bpstulist" "/usr/openv/volmgr/bin/tpconfig -d" "/usr/openv/volmgr/bin/tpclean" "/usr/openv/netbackup/bin/goodies/available_media" "/usr/openv/netbackup/bin/admincmd/bpcatlist -since-days 15";do
	case $command in
	"/usr/openv/netbackup/bin/admincmd/bpgetconfig"|"/usr/openv/netbackup/bin/admincmd/bpminlicense -verbose"|"/usr/openv/netbackup/bin/admincmd/bpstulist"|"/usr/openv/netbackup/bin/admincmd/bpcatlist -since-days 15") if [[ -e /usr/openv/netbackup/bin/admincmd ]];then HREF;P_CMD "$command";P_TOP;cmd "$command";P_BOT;fi;;
	"/usr/openv/volmgr/bin/tpconfig -d"|"/usr/openv/volmgr/bin/tpclean")
	 if [[ -e /usr/openv/volmgr/bin ]];then
		HREF;P_CMD "$command";P_TOP
		if [[ -n `$command` ]];then cmd "$command";else P;fi
		P_BOT;fi;;
	"/usr/openv/netbackup/bin/goodies/available_media") if [[ -e /usr/openv/netbackup/bin/goodies/available_media ]];then HREF;P_CMD "$command";P_TOP;cmd "$command";P_BOT;fi;;
	*) HREF;P_CMD "$command";P_TOP;cmd "$command";P_BOT;;
	esac
 done
fi

RM "${LOG}.log"
for pid in `ps -ef|grep lsinventory|grep -v java|grep -v grep|grep -v Done|awk '{print $2}'`;do
[[ -n "$pid" ]] && kill -9 $pid 2>/dev/null
done
RM "$LOG.pv"
[[ -d "hsperfdata_oracle" ]] && rm -fr "hsperfdata_oracle"
$E "Information collecting complete successfully!"
$E "Information output: $LOG"
P_MARK "=";$E "Finished : `date`"
STARTH=`$E $STARTH|sed -r 's/0+([1-9])/\1/g'`
TIANYIm=`$E $TIANYIm|sed -r 's/0+([1-9])/\1/g'`
STARTS=`$E $STARTS|sed -r 's/0+([1-9])/\1/g'`
ENDH=`$E $(date +%H)|sed -r 's/0+([1-9])/\1/g'`
ENDM=`$E $(date +%M)|sed -r 's/0+([1-9])/\1/g'`
ENDS=`$E $(date +%S)|sed -r 's/0+([1-9])/\1/g'`
((DH=$ENDH-$STARTH))
[[ $DH -lt 0 ]] && ((DH=$DH+24))
if [[ $ENDM -lt $TIANYIm ]];then ((DH=$DH-1));((DM=$ENDM+60-$TIANYIm));else ((DM=$ENDM-$TIANYIm));fi
if [[ $ENDS -lt $STARTS ]];then ((DM=$DM-1));((DS=$ENDS+60-$STARTS));else ((DS=$ENDS-$STARTS));fi
$E "Use Time : $DH Hours  $DM Minutes  $DS Seconds"
$E ""
