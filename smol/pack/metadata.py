"""
The pack metadata service. Stores metadata and handles querying for updates.
"""

# There are 4 types of packs:
# * Packs from manifests
# * Packs from direct URLs
# * Packs from files
# * Virtual Packs
#
# Manifest packs are the nicest. We can just grab the manifest on a "schedule"
# and update the upstram pack metadata from that. We also have the potential for
# multiple versions being available.
#
# Direct URL packs we have to use HTTP caching mechanisms (ETag, Last-Modified),
# in order to detect updates. If we want old versions, we have to keep them on 
# disk.
#
# File packs are just hopeless. No features at all.
#
# Virtual packs have no concrete pack files, but instead are base platform packs,
# ie Vanilla (Beta, Alpha), Forge, etc.