// SPDX-License-Identifier: MIT
// Narrow, read-only PKG extraction via the separately licensed LibOrbisPkg DLL.
using System;
using System.IO;
using System.IO.MemoryMappedFiles;
using System.Linq;
using LibOrbisPkg.PKG;
using LibOrbisPkg.PFS;

class ExtractCode
{
    static int Main(string[] args)
    {
        if (args.Length != 2 && !(args.Length == 3 && args[2] == "--all"))
        {
            Console.Error.WriteLine("Usage: ExtractCode.exe input.pkg output-directory [--all]");
            return 2;
        }
        try
        {
            string output = Path.GetFullPath(args[1]).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar;
            if (Directory.Exists(output) && Directory.EnumerateFileSystemEntries(output).Any())
                throw new IOException("Use an empty output directory");
            Directory.CreateDirectory(output);
            // A read-only mapping prevents changes to the user's original package.
            using (var input = new FileStream(args[0], FileMode.Open, FileAccess.Read, FileShare.Read))
            using (var mm = MemoryMappedFile.CreateFromFile(input, null, 0, MemoryMappedFileAccess.Read, System.IO.HandleInheritability.None, false))
            {
                Pkg pkg;
                using (var stream = mm.CreateViewStream(0, 0, MemoryMappedFileAccess.Read))
                    pkg = new PkgReader(stream).ReadPkg();
                using (var view = mm.CreateViewAccessor((long)pkg.Header.pfs_image_offset, (long)pkg.Header.pfs_image_size, MemoryMappedFileAccess.Read))
                {
                    var outer = new PfsReader(view, pkg.Header.pfs_flags, pkg.GetEkpfs());
                    var inner = new PfsReader(new PFSCReader(outer.GetFile("pfs_image.dat").GetView()));
                    int count = 0;
                    foreach (var file in inner.GetAllFiles())
                    {
                        string relative = file.FullName.Replace('\\', '/').TrimStart('/');
                        if (args.Length != 3 && !(file.name == "eboot.bin" || file.name.EndsWith(".prx", StringComparison.OrdinalIgnoreCase) || file.name.EndsWith(".sprx", StringComparison.OrdinalIgnoreCase)))
                            continue;
                        string target = Path.GetFullPath(Path.Combine(output, relative));
                        if (!target.StartsWith(output, StringComparison.OrdinalIgnoreCase))
                            throw new InvalidDataException("Package path escapes output directory");
                        if (System.IO.File.Exists(target))
                            throw new IOException("Refusing to overwrite existing file: " + target);
                        Directory.CreateDirectory(Path.GetDirectoryName(target));
                        file.Save(target);
                        Console.WriteLine(relative + "\t" + file.size);
                        ++count;
                    }
                    Console.WriteLine("Extracted " + count + " files (mode: " + (args.Length == 3 ? "all" : "code") + ").");
                }
            }
            return 0;
        }
        catch (Exception e)
        {
            Console.Error.WriteLine("Extraction failed: " + e.Message);
            return 1;
        }
    }
}
