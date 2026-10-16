# MaxamoRooter (Bulk)

**MaxamoRooter (Bulk)** is a powerful Blender add-on designed to batch-process Mixamo character meshes and animations, injecting a proper `root` bone and remapping animation curves for flawless **Unreal Engine 5 (UE5) Root Motion**.

---

## The Problem It Solves
Mixamo characters and animations lack a standard `root` bone—all world translation is stored directly on the `Hips` bone. When imported into Unreal Engine, this prevents proper root motion and causes retargeting conflicts. 

Manually editing individual FBX files or writing custom scripts for dozens of animations is tedious. **MaxamoRooter** automates this entirely in bulk directly from Blender's UI sidebar.

---

## ✨ Key Features
*   **Bulk Character Processing:** Inject a root bone at the world origin (`0,0,0`), parent the `Hips` bone, and batch-export clean skeletal meshes.
*   **Bulk Animation Processing:** Automatically create the root bone and remap animation tracks (Hips X $\rightarrow$ Root X, Hips Z $\rightarrow$ Root Y) for valid UE5 root motion.
*   **Memory Leak Protection:** Features an internal cleanup routine that purges cached actions, meshes, and armatures between iterations to prevent data duplication across batch exports.
*   **Intuitive UI Panel:** Seamlessly integrated into the 3D Viewport sidebar (`N-Panel > MaxamoRooter`).

---

## 📥 Installation

1. Download or clone this repository and grab the `mixamo_root_tool.py` file (or zip it).
2. Open Blender (v4.0 or newer).
3. Go to **Edit > Preferences > Add-ons**.
4. Click the install dropdown/button in the top right, select `mixamo_root_tool.py`, and click **Install Add-on**.
5. Enable **MaxamoRooter (Bulk)** in your add-on list.

---

## 🎮 How to Use

1. Press **N** in your Blender 3D Viewport and open the **MaxamoRooter** tab.
2. Select your destination **Output Directory** using the folder browser.
3. Click **Bulk Fix Characters** or **Bulk Fix Animations**.
4. A multi-select file browser will open. Select your target Mixamo FBX files and execute.
5. Import your clean, rooted assets directly into Unreal Engine 5!

---

## 🛠️ Recommended UE5 FBX Export / Import Settings
*   **Blender Export:** Ensure *Add Leaf Bones* is **unchecked**.
*   **UE5 Import:** Ensure your character mesh and animations share the same newly injected root hierarchy for smooth IK Retargeting.

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.
