library(jsonlite)
library(tidyverse)


names <- c("Motivation", "Background", "Research Gaps", "Methods & Results")
categorize <- function(n) {
  return(names[n])
}

pdata <- fromJSON("data/plos-cb-categorized.json") |>
  as_tibble() |>
  pivot_longer(
    cols = c(abstract, introduction), 
    names_to = "section", 
    values_to = "data"
  ) |>
  mutate(nrows = map(data, nrow)) |>           
  mutate(hasrows = map_int(nrows, length)) |>   
  filter(hasrows == 1) |>
  unnest(data) |>
  drop_na(category) |>
  group_by(section, doi) |>
  mutate(section_length = max(position)) |>
  ungroup() |>
  mutate(relative_position = position / section_length)  |>
  mutate(word_list = map(sentence, ~ unlist(strsplit(., split = " ")))) |>
  mutate(word_count = map_int(word_list, ~ length(.))) |>
  mutate(category = map_chr(category, categorize)) |>
  mutate(category = factor(category, levels = names)) |>
  select(doi, date, section, sentence, position, category,
         section_length, relative_position, word_count)

write.csv(pdata, "data/plos-cb-tidy.csv")

category_kde <- pdata |>
  ggplot(aes(relative_position, color = category)) +
  facet_grid(cols = vars(str_to_title(section))) +
  geom_density(adjust = 2) + 
  labs(x = "Relative Position",
       y = "Density",
       color = "Category") +
  theme_bw() +
  theme(axis.ticks.y = element_blank(),
        axis.text.y = element_blank())

category_kde
ggsave("img/category-kde.png", width = 6, height = 4)

category_count <- pdata |>
  group_by(section, doi) |>
  count(category) |>
  ggplot(aes(n, color = category)) + 
  geom_boxplot() + 
  facet_grid(cols = vars(str_to_title(section)), 
             rows = vars(category),
             scales = "free_x") +
  labs(x = "Number of Sentences") +
  theme_bw() + 
  xlim(0, NA) +
  theme(axis.ticks.y = element_blank(),
        axis.text.y = element_blank(),
        legend.position = "none")
 
category_count
ggsave("img/category-count.png", width = 6, height = 6)

section_length <- pdata |>
  group_by(section, doi) |>
  summarize(Sentences = max(position),
            Words = sum(word_count)) |>
  pivot_longer(cols = c("Sentences", "Words"), 
               names_to="Metric", 
               values_to="Count")  |>
  ggplot(aes(y = Count)) +
  geom_boxplot() +
  facet_wrap(vars(str_to_title(section), Metric), 
             scales = "free_y") + 
  labs(y = "Count") +
  theme_bw() +
  theme(axis.ticks.x = element_blank(),
        axis.text.x = element_blank())

section_length
ggsave("img/section-count.png", width = 6, height = 6)


