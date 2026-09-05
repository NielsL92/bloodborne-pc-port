# Environment recorded for P0
Recorded 2026-09-05. Hardware source: local/runs/20260905-prior-evidence/host.json; Vulkan and NVIDIA command outputs have individual run manifests.

| Component | Observed |
| --- | --- |
| OS | Windows 11 Home, 10.0.26200 |
| CPU | Intel Core i7-13700K, 16 cores / 24 logical processors |
| Memory | 33,335,168 KiB OS-visible (31.79 GiB); 4,667,632 KiB free at initial sample |
| GPU | RTX 4090; nvidia-smi reports 24,564 MiB; driver 610.47 |
| Vulkan | NVIDIA Vulkan 1.4.341; Intel UHD 770 also enumerated, Vulkan 1.3.240 |
| Validation | Khronos validation layer not installed; loader warns on a layer registry lookup but enumerates both devices successfully |
| E: | NTFS, 2,000,381,014,016 bytes total; 1,288,259,436,544 initially free; physical storage is an HDD |
| MSVC | Existing VS 18 Build Tools, toolset 14.51.36231 |
| Windows SDK | Existing 10.0.26100.0 |
| Git | 2.54.0.windows.1 |
| Python | Existing C:/Python314 and project .venv; Capstone 5.0.6 |
| New local tools | LLVM 21.1.8 full x64 Windows SDK, CMake 4.2.3, Ninja 1.13.2; official release digests verified |
| WSL | wsl.exe exists; it reports WSL is not installed |
| Build concurrency | Two workers per active build; revisit after measured memory use |

The authored Windows LLVM object probe passes 1,000 callback/memory cases. It records CPUID leaf 1 ECX 0xfffaf38b, leaf 7 EBX 0x239c27a9, extended ECX 0x121 and XCR0 0x7, establishing OS-enabled XMM/YMM state and the AVX2/BMI/FMA-related host features required by the baseline. This probe is not Remill output or a game test.

The legacy Win32_VideoController AdapterRAM field overflows at 4 GiB and was not used for RTX VRAM. Use nvidia-smi/Vulkan values above.

Tool entry point: .venv/Scripts/python.exe tools/dev.py TOOL ARGS. This obtains the existing vcvars64 environment and prepends only the project toolchain paths. It does not change the system PATH or install another IDE. Exact download URLs/digests: reports/toolchain-downloads.json.

The native Windows Remill attempt uses source 56918a8c2554088e93389e97d292f4035286506c and the prebuilt LLVM SDK through USE_EXTERNAL_LLVM=ON. Its default source superbuild pins LLVM 17.0.6; use of external LLVM 21.1.8 is an explicit experiment, not assumed compatibility. Native gflags/glog/googletest/XED dependencies have built. The SDK omits SPARC codegen libraries; the preserved patches/remill-windows-sdk.patch makes their unused linkage conditional.

Sandbox hardware queries were denied. Subsequently the sandbox helper itself failed to start repeatedly (setup refresh had errors). Approved host commands continue to work; no permission review rejection or user intervention occurred.
