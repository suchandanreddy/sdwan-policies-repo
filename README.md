
# Cisco SD-WAN policies

# Objective 

*   How to use vManage APIs to - 
    - Create DC preference and Hub-n-Spoke policy
    - Create Application Aware Routing policy for audio-and-video application family

# Requirements

To use this code you will need:

* Python 3.7+
* vManage user login details. (User should have privilege level to configure policies)

# Install and Setup

- Clone the code to local machine.

```
git clone https://github.com/suchandanreddy/sdwan-policies-repo.git
cd sdwan-policies-repo
```
- Setup Python Virtual Environment (requires Python 3.7+)

```
python3.7 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

- Create **config_details.yaml** using below sample format to provide the login details of vManage and inputs for centralised policy

## Example:

```
# vManage Connectivity Info

vmanage_host: 
vmanage_port: 
vmanage_username: 
vmanage_password: 

#DC1 pref over DC2  policy

DC1_site_id: 100
DC2_site_id: 1001
Spokes_site_id: 1002-1003

#Audio Video AAR policy

Site_id: 1001-1003
Service_VPNs: 1
Latency: 400
Loss: 2
Jitter: 5
pref_color: mpls
backup_pref_color: private1
```

## Sample Outputs

```
(venv) % python3 create-policies.py
Policy List Updates: 6
Policy Definition Updates: 4
Central Policy Updates: 1
Local Policy Updates: 0
```

## Sample policy created

```
policy
  sla-class Audio-and-Video-SLA-Class
   latency 400
   loss 2
   jitter 5
  !
 control-policy DC1-Pref-over-DC2-Policy
    sequence 1
     match route
      site-list DC1-Site-list
      prefix-list _AnyIpv4PrefixList
     !
     action accept
      set
       preference 100
      !
     !
    !
    sequence 11
     match route
      site-list DC2-Site-list
      prefix-list _AnyIpv4PrefixList
     !
     action accept
      set
       preference 75
      !
     !
    !
    sequence 21
     match tloc
      site-list DC1-Site-list
     !
     action accept
     !
    !
    sequence 31
     match tloc
      site-list DC2-Site-list
     !
     action accept
     !
    !
  default-action reject
 !
 control-policy Block-DC2-to-DC1-Tunnels
    sequence 1
     match tloc
      site-list DC1-Site-list
     !
     action reject
     !
    !
  default-action accept
 !
 app-route-policy _Corp-VPN-List_Audio-V_502939736
  vpn-list Corp-VPN-List
    sequence 1
     match
      app-list audio-video-app-list
      source-ip 0.0.0.0/0
     !
     action
      sla-class Audio-and-Video-SLA-Class  preferred-color mpls
      backup-sla-preferred-color private1
     !
    !
 !
 control-policy Block-DC1-to-DC2-Tunnels
    sequence 1
     match tloc
      site-list DC2-Site-list
     !
     action reject
     !
    !
  default-action accept
 !
 lists
  app-list audio-video-app-list
   app-family audio-video 
   app-family audio_video 
  !
  site-list AAR-Sites-list
   site-id 1001-1003 
  !
  site-list DC1-Site-list
   site-id 100 
  !
  site-list DC2-Site-list
   site-id 1001 
  !
  site-list Spokes-list
   site-id 1002-1003 
  !
  vpn-list Corp-VPN-List
   vpn 1 
  !
  prefix-list _AnyIpv4PrefixList
   ip-prefix 0.0.0.0/0 le 32 
  !
 !
!
apply-policy
 site-list Spokes-list
  control-policy DC1-Pref-over-DC2-Policy out
 !
 site-list AAR-Sites-list
  app-route-policy _Corp-VPN-List_Audio-V_502939736
 !
 site-list DC2-Site-list
  control-policy Block-DC2-to-DC1-Tunnels out
 !
 site-list DC1-Site-list
  control-policy Block-DC1-to-DC2-Tunnels out
 !
!
```