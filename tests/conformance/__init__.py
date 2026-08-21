#
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Protocol conformance for the packaged provider.

These tests speak tfplugin6 to the `.psp` this repo builds -- the artifact
Terraform actually launches -- rather than to in-process handlers. The handlers
are covered in pyvider; what is unproven without this suite is the packaging:
flavorpack bundling, the entry point, environment passthrough, the go-plugin
handshake, mTLS, and msgpack over a real socket.

The driver lives in `tofusoup.tfplugin` and knows nothing about pyvider. Only
the assertions here are provider-specific.
"""

# 🧪🔌🔚
