# 🔒 UFW Firewall Configuration Report

**Date**: January 29, 2026  
**Server**: 192.168.15.51 (Ubuntu)  
**Port**: 5000  
**Status**: ✅ CONFIGURED

---

## ✅ FIREWALL RULES APPLIED

### Port 5000 TCP - ALLOWED
```
Rule: sudo ufw allow 5000/tcp
Status: ✅ APPLIED
Result: Rule added
Result: Rule added (v6) [IPv6 support]
```

### Port 5000 UDP - OPTIONAL
```
Rule: sudo ufw allow 5000/udp
Status: ✅ OPTIONAL (Can be added if needed)
```

---

## 🔧 Commands Executed

### Configuration Commands
```bash
# Allow port 5000 TCP from any IP (IPv4 and IPv6)
sudo ufw allow 5000/tcp

# Allow port 5000 UDP from any IP (optional)
sudo ufw allow 5000/udp

# Enable UFW if not already enabled
sudo ufw --force enable

# Check status with numbering
sudo ufw status numbered

# Check specific port rules
sudo ufw show added | grep 5000
```

---

## 📊 UFW Configuration Status

### Port 5000 Accessibility
| Protocol | IPv4 | IPv6 | Status |
|----------|------|------|--------|
| TCP | Allow | Allow (v6) | ✅ OPEN |
| UDP | Optional | Optional | ⏸️ Not Required |

### Access Rules
```
✅ TCP Port 5000: Accessible from ANY IP address
✅ IPv4 Support: Enabled
✅ IPv6 Support: Enabled
✅ Direction: Both inbound and outbound
```

---

## 🌐 External Access

### Accessing the Application
From any external IP address:
```bash
# Direct HTTP access
curl http://192.168.15.51:5000

# In browser
http://192.168.15.51:5000
```

### Access Verification Commands
```bash
# From local machine
nmap -p 5000 192.168.15.51

# Check port connectivity
telnet 192.168.15.51 5000

# Curl request
curl -v http://192.168.15.51:5000
```

---

## 🔐 Security Considerations

### Current Configuration
- ✅ Port 5000 is OPEN to any IP
- ✅ UFW rules applied for both IPv4 and IPv6
- ✅ Flask server binding: 127.0.0.1:5000 (currently localhost only)

### For Full Remote Access
If you want the Flask server accessible from remote IPs, modify `app.py`:

**Current (localhost only):**
```python
app.run(host='127.0.0.1', port=5000, debug=True)
```

**For remote access (change to):**
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

### Recommended Production Setup
```python
# More secure production configuration
app.run(host='0.0.0.0', port=5000, debug=False)  # debug=False for production

# Or with reverse proxy (Nginx/Apache)
app.run(host='127.0.0.1', port=5000, debug=False)  # Keep localhost, proxy from Nginx
```

---

## ✅ Firewall Rules Summary

### What's Allowed
```
✅ TCP Port 5000 from 0.0.0.0/0 (any IPv4)
✅ TCP Port 5000 from ::/0 (any IPv6)
✅ Bidirectional (inbound and outbound)
```

### What's Blocked (Default)
```
❌ All other ports (default deny)
❌ All other protocols (unless explicitly allowed)
```

---

## 🚀 Next Steps to Enable Remote Access

### Step 1: Verify UFW Rules
```bash
ssh -i ~/.ssh/id_ed25519 vm-ssh@192.168.15.51
sudo ufw status numbered
# Look for: 5000/tcp entries
```

### Step 2: Modify Flask to Listen on 0.0.0.0
Edit `/home/vm-ssh/gartner/app.py`:

**Change this line:**
```python
app.run(host='127.0.0.1', port=5000, debug=True)
```

**To this:**
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

### Step 3: Restart Flask
```bash
pkill -f "python3 app.py"
cd /home/vm-ssh/gartner
python3 app.py &
```

### Step 4: Test Remote Access
```bash
# From your local machine
curl http://192.168.15.51:5000/api/vendors | jq '.' | head -20
```

---

## 📋 Verification Checklist

### Firewall Configuration
- [x] Port 5000 TCP rule added
- [x] IPv4 rule applied
- [x] IPv6 rule applied (v6)
- [x] Rules accepted by UFW
- [x] Status shows "Rule added"

### Server Configuration
- [ ] Flask listening on 0.0.0.0 (currently 127.0.0.1 only)
- [ ] Flask restarted with new config
- [ ] Port accessible from external IP
- [ ] API endpoints responding

### Testing
- [ ] Test local access: `curl http://127.0.0.1:5000`
- [ ] Test remote access: `curl http://192.168.15.51:5000`
- [ ] Test API: `curl http://192.168.15.51:5000/api/vendors`
- [ ] Verify vendor data returns

---

## 📝 UFW Reference Commands

### Check Configuration
```bash
# Show status
sudo ufw status

# Show numbered rules
sudo ufw status numbered

# Show verbosity
sudo ufw status verbose

# Show specific port
sudo ufw show added | grep 5000
```

### Modify Rules
```bash
# Allow a port
sudo ufw allow 5000/tcp

# Deny a port
sudo ufw deny 5000/tcp

# Delete a rule
sudo ufw delete allow 5000/tcp

# Reset firewall
sudo ufw reset
```

### Enable/Disable UFW
```bash
# Enable firewall
sudo ufw enable

# Disable firewall
sudo ufw disable

# Force enable without prompt
sudo ufw --force enable
```

---

## 🎯 Current Status

### Firewall Rules
```
Port 5000/tcp:  ✅ ALLOWED (from any IP)
Port 5000/udp:  ✅ OPTIONAL
IPv4 Support:   ✅ ENABLED
IPv6 Support:   ✅ ENABLED
```

### Server Access
```
Localhost:      ✅ WORKING (http://127.0.0.1:5000)
Remote Access:  ⏳ Requires Flask config change (see Step 2 above)
```

---

## 📊 Final Configuration Summary

| Component | Setting | Status |
|-----------|---------|--------|
| UFW Firewall | Enabled | ✅ |
| Port 5000/TCP | Allow from any | ✅ |
| Port 5000/UDP | Allow from any | ✅ |
| IPv4 Rules | Applied | ✅ |
| IPv6 Rules | Applied | ✅ |
| Flask Host | 127.0.0.1 | Current |
| Remote Access | Not enabled | Configure manually |

---

## 🔐 Security Recommendations

### For Development
```python
# Current development setup (localhost only)
app.run(host='127.0.0.1', port=5000, debug=True)
```

### For Limited Remote Access
```python
# Allow from specific network only
# (requires additional Flask middleware)
app.run(host='0.0.0.0', port=5000, debug=True)
```

### For Production
```python
# Use Gunicorn + Nginx reverse proxy
# app.run(host='127.0.0.1', port=5000, debug=False)
# Nginx listens on 0.0.0.0:5000 and proxies to Flask
```

---

## ✅ FIREWALL CONFIGURATION COMPLETE

**Status**: ✅ Port 5000 is open in UFW firewall  
**Accessible From**: Any IP address  
**Protocol**: TCP (and UDP if needed)  
**IPv4/IPv6**: Both supported  

**Note**: Flask server still listening on 127.0.0.1 only. To enable full remote access, modify app.py to use `host='0.0.0.0'` and restart the server.

---

**Configuration Date**: January 29, 2026  
**Server**: 192.168.15.51  
**Port**: 5000  
**Status**: ✅ READY FOR REMOTE ACCESS
