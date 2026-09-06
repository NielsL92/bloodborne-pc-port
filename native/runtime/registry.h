// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include "runtime.h"
namespace bb_registry {
extern const bb_runtime::Tables tables;
extern const bb_runtime::X87Site x87_sites[];
extern const size_t x87_site_count;
extern const bb_runtime::Target import_gateways[];
extern const size_t import_gateway_count;
}
