// Machbarkeitstest TIA Portal Openness (V21):
// Öffnet das Projekt ohne Oberfläche, listet Geräte, PLC-Datentypen und Programmbausteine, schließt wieder.
// Ändert nichts am Projekt.
//
// Übersetzen (x64, wegen der Siemens-DLLs):  tools\openness\build.cmd
// Aufruf:  tools\openness\TiaProbe.exe [Projektdatei]
//          Standard: C:\TIA\SortingLine\SortingLine.ap21
// Voraussetzung: Benutzer ist in der Gruppe "Siemens TIA Openness", TIA Portal hat das Projekt NICHT geöffnet.

using System;
using System.IO;
using System.Reflection;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Blocks;
using Siemens.Engineering.SW.Types;

class TiaProbe
{
    const string PublicApiDir = @"C:\Program Files\Siemens\Automation\Portal V21\PublicAPI\V21\net48";
    const string DefaultProject = @"C:\TIA\SortingLine\SortingLine.ap21";

    static int Main(string[] args)
    {
        // Siemens-DLLs aus dem Installationsverzeichnis laden statt aus dem Programmordner
        AppDomain.CurrentDomain.AssemblyResolve += ResolveSiemensAssembly;
        try
        {
            return Run(args.Length > 0 ? args[0] : DefaultProject);
        }
        catch (Exception ex)
        {
            Console.WriteLine("FEHLER: " + ex.GetType().Name + ": " + ex.Message);
            return 1;
        }
    }

    static Assembly ResolveSiemensAssembly(object sender, ResolveEventArgs e)
    {
        string file = Path.Combine(PublicApiDir, new AssemblyName(e.Name).Name + ".dll");
        return File.Exists(file) ? Assembly.LoadFrom(file) : null;
    }

    static int Run(string projectPath)
    {
        Console.WriteLine("Prozess: " + (Environment.Is64BitProcess ? "64 Bit" : "32 Bit"));
        Console.WriteLine("Starte TIA Portal ohne Oberfläche ...");

        using (TiaPortal tia = new TiaPortal(TiaPortalMode.WithoutUserInterface))
        {
            Console.WriteLine("Öffne " + projectPath);
            Project project = tia.Projects.Open(new FileInfo(projectPath));
            try
            {
                foreach (Device device in project.Devices)
                {
                    Console.WriteLine("Gerät: " + device.Name);
                    foreach (DeviceItem item in device.DeviceItems)
                    {
                        PlcSoftware plc = FindPlcSoftware(item);
                        if (plc == null) continue;

                        Console.WriteLine("  PLC-Software: " + plc.Name);
                        Console.WriteLine("  PLC-Datentypen:");
                        PrintTypes(plc.TypeGroup.Types, plc.TypeGroup.Groups, "    ");
                        Console.WriteLine("  Programmbausteine:");
                        PrintBlocks(plc.BlockGroup.Blocks, plc.BlockGroup.Groups, "    ");
                    }
                }
            }
            finally
            {
                project.Close();
            }
        }

        Console.WriteLine("OK");
        return 0;
    }

    static PlcSoftware FindPlcSoftware(DeviceItem item)
    {
        SoftwareContainer container = item.GetService<SoftwareContainer>();
        if (container != null && container.Software is PlcSoftware)
            return (PlcSoftware)container.Software;

        foreach (DeviceItem child in item.DeviceItems)
        {
            PlcSoftware found = FindPlcSoftware(child);
            if (found != null) return found;
        }
        return null;
    }

    static void PrintBlocks(PlcBlockComposition blocks, PlcBlockUserGroupComposition groups, string indent)
    {
        foreach (PlcBlock block in blocks)
            Console.WriteLine(indent + block.Name + " (" + block.GetType().Name + " " + block.Number + ")");
        foreach (PlcBlockUserGroup group in groups)
        {
            Console.WriteLine(indent + "[" + group.Name + "]");
            PrintBlocks(group.Blocks, group.Groups, indent + "  ");
        }
    }

    static void PrintTypes(PlcTypeComposition types, PlcTypeUserGroupComposition groups, string indent)
    {
        foreach (PlcType type in types)
            Console.WriteLine(indent + type.Name);
        foreach (PlcTypeUserGroup group in groups)
        {
            Console.WriteLine(indent + "[" + group.Name + "]");
            PrintTypes(group.Types, group.Groups, indent + "  ");
        }
    }
}
