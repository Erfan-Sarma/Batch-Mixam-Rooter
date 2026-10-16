# MixamoRooter (Bulk) 🚀

**MixamoRooter (Bulk)** is a powerful Blender add-on designed to batch-process Mixamo character meshes and animations, injecting a proper `root` bone and remapping animation curves for flawless **Unreal Engine 5 (UE5) Root Motion** in large quantities.

---

## 🎯 Motivation & Philosophy
My intention was to simply add the missing `root` bone to Mixamo characters and animations so they are much easier to use in Unreal Engine. Specifically, this allows you to seamlessly retarget external Mixamo animations to standard UE skeletons (like the Mannequin) and use UE-compatible skeletons with external animation libraries. 

For this purpose, the best practice I found was to handle the structural bone injection and channel mapping cleanly inside Blender, and then let Unreal Engine handle the rest via its powerful IK Retargeter system. This bulk tool automates that workflow across entire folders of assets.

---

## ✨ Key Features
*   **Bulk Character Processing:** Inject a root bone at the world origin (`0,0,0`), parent the `Hips` bone, and batch-export clean skeletal meshes.
*   **Bulk Animation Processing:** Automatically create the root bone and remap animation tracks (Hips X $\rightarrow$ Root X, Hips Z $\rightarrow$ Root Y) for valid UE5 root motion across multiple files.
*   **Memory Leak Protection:** Features an internal cleanup routine that purges cached actions, meshes, and armatures between iterations to prevent data duplication across batch exports.
*   **Intuitive UI Panel:** Seamlessly integrated into the 3D Viewport sidebar (`N-Panel > MixamoRooter`).

---

## 📦 Prefer Single-Asset Processing?
If you only need to process assets one by one inside Blender scenes, check out the single version:
👉 **[MixamoRooter (Single) Repository](https://github.com/Erfan-Sarma/MixamoRooter)**

---

## 📥 Installation

1. Download or clone this repository and grab the `mixamo_root_tool.py` file.
2. Open Blender (v4.0 or newer).
3. Go to **Edit > Preferences > Add-ons**.
4. Click the install button in the top right, select `mixamo_root_tool.py`, and click **Install Add-on**.
5. Enable **MixamoRooter (Bulk)** in your add-on list.

---

## 🎮 How to Use

1. Press **N** in your Blender 3D Viewport and open the **MixamoRooter** tab.
2. Select your destination **Output Directory** using the folder browser.
3. Click **Bulk Fix Characters** or **Bulk Fix Animations**.
4. A multi-select file browser will open. Select your target Mixamo FBX files and execute.
5. Import your clean, rooted assets directly into Unreal Engine 5!

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.
