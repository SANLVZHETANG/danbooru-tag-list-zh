使用deepseek的api对danbooru的通用概念词条进行了汉化，tag补全功能可以在comfyui中使用，需要配合
[ComfyUI-Custom-Scripts](https://github.com/pythongosssss/ComfyUI-Custom-Scripts) 。
教程：
1.找到Custom-Scripts的设置选项。
![2](./图片/2.png)
2.清除原来的文本并粘贴txt里的内容，然后保存。
![3](./图片/3.png)
3.如果成功，你应该会看到以下画面。
![1](./图片/1.png)
---
/以下是原作者的readme/
---
I was looking for an updated danbooru tag list but I couldn't find a recent one that was in the correct format, so I made my own.

Based on this original script: https://gist.github.com/bem13/596ec5f341aaaefbabcbf1468d7852d5

requires the requests library (`pip install requests`)

Main Changes:
- Allows setting minimum post threshold
- Allows '-' format (found to be better for prompt following)
- Saves tag categories (used by SwarmUI and tag-complete)
- Uses the UI's expected formatting
- Slightly faster rate limit
- Ability to exclude tag categories
- The option to include aliases (UI support varies)
- supports pulling tags from e621 (optional)

About the uploaded lists:

I've uploaded premade versions of every all-category list with the minimum threshold set to 50, and aliases enabled. Aliases are only currently supported for danbooru because e621 has way too many and some overlap with real danbooru tags. There's some half working commented out code that will also pull aliases from e621 which I might support for e621-only lists, but for now I don't want to look at any more furry art.

The format is as follows:

|tag|category|post count|aliases(if enabled)|
|---|--------|----------|-----------------------------------------|
