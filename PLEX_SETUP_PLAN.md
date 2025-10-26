# Plex Server Setup Plan - Raspberry Pi 5

## Current Status Analysis

### ✅ What's Working
- Docker container is running successfully
- Plex Media Server started and listening on port 32400
- RPi5 connected to network at `192.168.0.131` (WiFi)
- Docker networking properly configured

### ❌ Current Issues
1. **Server Unclaimed**: No claim token set - server not linked to your Plex account
2. **Network Access**: Server only accessible locally, not from other devices
3. **No Media Libraries**: Not configured yet
4. **Performance**: Not optimized for RPi5 limitations

## Implementation Plan

### Phase 1: Server Claiming & Basic Access (30 minutes)

**Priority: HIGH - Must be done immediately**

1. **Get Claim Token**
   - Visit https://plex.tv/claim
   - Copy token (expires in 4 minutes!)
   - Format: `claim-xxxxxxxxxxxxxxxxx`

2. **Update Docker Configuration**
   - Add `PLEX_CLAIM` environment variable
   - Set `ADVERTISE_IP=http://192.168.0.131:32400/`
   - Configure proper port mapping

3. **Restart Container**
   - `docker-compose down`
   - `docker-compose up -d`
   - Monitor logs for successful claiming

**Expected Result**: Access Plex at `http://192.168.0.131:32400/web`

### Phase 2: Storage & Media Setup (45 minutes)

1. **Prepare Storage Structure**
   ```bash
   # Create directories
   sudo mkdir -p /home/shane/plex/{config,transcode}
   sudo mkdir -p /media/external
   
   # Set permissions
   sudo chown -R 1000:1000 /home/shane/plex/
   ```

2. **Configure External Storage**
   - Connect USB drive/SSD for media
   - Mount to `/media/external`
   - Update fstab for persistent mounting

3. **Library Organization**
   - Create folder structure: Movies, TV Shows, Music
   - Follow Plex naming conventions

### Phase 3: Network Optimization (30 minutes)

1. **Static IP Configuration**
   - Set static IP `192.168.0.131`
   - Prevent IP changes affecting setup

2. **Router Configuration**
   - Port forward 32400 for external access
   - Enable UPnP if available
   - Test remote connectivity

### Phase 4: Performance Optimization (20 minutes)

1. **Hardware Acceleration Setup**
   - ⚠️ **Important**: RPi5 has NO hardware video encoding
   - Configure for CPU-only transcoding
   - Set realistic performance expectations

2. **Transcoding Settings**
   - Point transcode temp to external storage
   - Limit concurrent transcoding streams
   - Optimize quality settings for RPi5

3. **Media Format Optimization**
   - Prioritize H.264/AAC formats for direct play
   - Avoid formats requiring transcoding
   - Consider pre-transcoding 4K content

## Technical Considerations

### RPi5 Limitations
- **No Hardware Video Encoding**: CPU-only transcoding
- **Performance Ceiling**: 1-2 simultaneous 1080p transcodes max
- **4K Transcoding**: Not recommended
- **Direct Play**: Multiple 4K streams supported

### Network Architecture
- **Current**: WiFi connection at 192.168.0.131
- **Recommended**: Ethernet for better streaming performance
- **Port Requirements**: 32400 (primary), additional ports for discovery

### Storage Strategy
- **System**: Use SD card for OS/config only
- **Media**: External USB 3.0 SSD recommended
- **Transcode**: External storage to reduce SD card wear

## Risk Assessment

### High Risk
- **Claim Token Expiry**: 4-minute window to apply token
- **Network Instability**: WiFi connection may cause streaming issues

### Medium Risk
- **Storage Failure**: SD card wear from transcoding
- **Performance Issues**: Overloading CPU with transcoding

### Low Risk
- **Configuration Errors**: Easily reversible
- **Port Conflicts**: Well-documented solutions

## Success Criteria

### Phase 1 Complete
- [ ] Server claimed to your Plex account
- [ ] Web interface accessible from network devices
- [ ] No "unclaimed server" errors in logs

### Phase 2 Complete
- [ ] Media libraries configured and scanning
- [ ] External storage properly mounted
- [ ] Directory structure organized

### Phase 3 Complete
- [ ] Remote access working from outside network
- [ ] Static IP configured and stable
- [ ] Router port forwarding active

### Phase 4 Complete
- [ ] Transcoding optimized for RPi5
- [ ] Performance monitoring in place
- [ ] Media formats optimized for direct play

## Next Steps & Questions

1. **Do you have external storage ready** for your media library?

2. **What types of media** will you primarily serve? (Movies, TV, 4K content?)

3. **How many concurrent users** do you expect? (affects transcoding strategy)

4. **Do you need remote access** from outside your home network?

5. **Would you prefer Ethernet connection** instead of WiFi for better performance?

## Emergency Recovery

If something goes wrong:
```bash
# Stop everything
docker-compose down

# Remove container (keeps data)
docker container rm plex

# Start fresh (reapply claim token)
docker-compose up -d
```

---
**Estimated Total Time**: 2-3 hours for complete setup
**Required Downtime**: ~10 minutes during container restart