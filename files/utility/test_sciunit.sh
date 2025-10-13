#!/bin/bash
set -e


sciunit create TestProject


echo -e "#!/bin/bash\necho Hello SciUnit" > hello_world.sh
chmod +x hello_world.sh
sciunit exec ./hello_world.sh

# Test that experiment was created
EXPERIMENTS=$(sciunit list)
if [ -z "$EXPERIMENTS" ]; then
    echo "No experiments found"
    exit 1
fi

echo "SciUnit test passed!"
