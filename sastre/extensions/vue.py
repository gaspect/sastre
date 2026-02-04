from pathlib import Path
from typing import Dict, List
from .base import BaseExtension

class Vue(BaseExtension):
    def name(self) -> str:
        return "Vue"

    def dev_dependencies(self) -> Dict[str, str]:
        return {
            "@astrojs/vue": "^5.0.0",
            "vue": "^3.5.0"
        }

    def dirs(self) -> List[Path]:
        return [
            Path("src/components")
        ]

    def files(self) -> Dict[Path, str]:
        vue_component = """<script setup>
import { ref } from 'vue'

const props = defineProps({
  initialCount: {
    type: Number,
    default: 0
  }
})

const count = ref(props.initialCount)
</script>

<template>
  <div class="vue-component">
    <p>Vue Counter: <strong>{{ count }}</strong></p>
    <button @click="count++">Increment Vue</button>
  </div>
</template>

<style scoped>
.vue-component {
  border: 1px solid #42b883;
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
}
button {
  background-color: #42b883;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}
</style>
"""
        return {
            Path("src/components/VueCounter.vue"): vue_component
        }

    def setup(self, project_dir: Path):
        config_path = project_dir / "astro.config.mjs"
        if config_path.exists():
            content = config_path.read_text(encoding="utf-8")
            if "vue" not in content:
                if "import { defineConfig } from 'astro/config';" in content:
                    content = content.replace(
                        "import { defineConfig } from 'astro/config';",
                        "import { defineConfig } from 'astro/config';\nimport vue from '@astrojs/vue';"
                    )
                
                if "integrations: [" in content:
                    content = content.replace(
                        "integrations: [",
                        "integrations: [vue(),"
                    )
                else:
                    if "defineConfig({" in content:
                        content = content.replace(
                            "defineConfig({",
                            "defineConfig({\n  integrations: [vue()],"
                        )
                config_path.write_text(content, encoding="utf-8")
