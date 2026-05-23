import os
import json
import xml.etree.ElementTree as ET


def fix_agent(state):

    print("\n" + "="*60)
    print("🔧 AGENT 5/8: FIX AGENT")
    print("="*60)
    print("⏳ Generating automated fixes...")

    findings = state[
        "prioritized_findings"
    ]

    repo_path = state[
        "repo_path"
    ]

    fixes = []

    print(f"📂 Scanning repository: {repo_path}")

    # ==================================================
    # NODE.JS PACKAGE.JSON SUPPORT
    # ==================================================

    package_json = os.path.join(
        repo_path,
        "package.json"
    )

    if os.path.exists(package_json):

        print("\n📦 Found package.json - Processing Node.js dependencies...")

        with open(package_json) as f:

            data = json.load(f)

        dependencies = data.get(
            "dependencies",
            {}
        )

        for finding in findings:

            package = finding.get(
                "package"
            )

            fixed_version = finding.get(
                "fixed_version"
            )

            if (
                package in dependencies
                and fixed_version
            ):

                print(
                    f"Updating {package} "
                    f"to {fixed_version}"
                )

                dependencies[
                    package
                ] = fixed_version

                fixes.append({

                    "package":
                    package,

                    "fixed_version":
                    fixed_version,

                    "status":
                    "updated"
                })

        data["dependencies"] = (
            dependencies
        )

        with open(package_json, "w") as f:

            json.dump(
                data,
                f,
                indent=2
            )

    # ==================================================
    # MAVEN POM.XML SUPPORT
    # ==================================================

    pom_file = os.path.join(
        repo_path,
        "pom.xml"
    )

    if os.path.exists(pom_file):

        print("\n📦 Found pom.xml - Processing Maven dependencies...")

        try:

            tree = ET.parse(pom_file)

            root = tree.getroot()

            namespace = {
                "m":
                "http://maven.apache.org/POM/4.0.0"
            }

            dependencies = root.findall(
                ".//m:dependency",
                namespace
            )

            for finding in findings:

                package = finding.get(
                    "package"
                )

                fixed_version = finding.get(
                    "fixed_version"
                )

                if (
                    not package
                    or not fixed_version
                ):
                    continue

                artifact_id = (
                    package.split(":")[-1]
                )

                for dep in dependencies:

                    artifact = dep.find(
                        "m:artifactId",
                        namespace
                    )

                    version = dep.find(
                        "m:version",
                        namespace
                    )

                    if (
                        artifact is not None
                        and version is not None
                    ):

                        if (
                            artifact.text
                            == artifact_id
                        ):

                            print(
                                f"Updating Maven "
                                f"{artifact_id} "
                                f"to "
                                f"{fixed_version}"
                            )

                            version.text = (
                                fixed_version
                            )

                            fixes.append({

                                "package":
                                package,

                                "fixed_version":
                                fixed_version,

                                "status":
                                "updated"
                            })

            tree.write(pom_file)

        except Exception as e:

            print(
                "\nMAVEN FIX ERROR\n"
            )

            print(str(e))

    # ==================================================
    # SUMMARY
    # ==================================================

    print(f"\n✅ Fix generation complete")
    print(f"   Total fixes generated: {len(fixes)}")
    
    if fixes:
        print(f"\n📝 Fixes applied:")
        for fix in fixes:
            print(f"   - {fix.get('package')}: {fix.get('fixed_version')} ({fix.get('status')})")
    else:
        print(f"   ⚠️  No automatic fixes available for this project type")

    state["generated_fixes"] = fixes

    return state